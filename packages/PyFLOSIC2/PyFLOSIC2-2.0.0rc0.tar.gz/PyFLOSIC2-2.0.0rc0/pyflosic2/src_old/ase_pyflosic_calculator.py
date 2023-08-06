# pyflosic-ase-calculator
#
# author:	S. Schwalbe
# task:  	ase calculator for pyflosic

import os
import numpy as np
from ase.calculators.calculator import FileIOCalculator, Parameters, kpts2mp, \
    ReadError
from ase.atom import Atom
from ase import Atoms
from ase.units import Ha, Bohr, Debye
try:
    from ase.atoms import atomic_numbers
except BaseException:
    # moved in 3.17 to
    from ase.data import atomic_numbers
import copy
from pyflosic2.src_old.flosic_os import xyz_to_nuclei_fod, ase2pyscf, flosic
from pyflosic2.src_old.flosic_scf import FLOSIC
from ase.calculators.calculator import Calculator


def force_max_lij(lambda_ij):
    #
    # calculate the RMS of the l_ij matrix
    #
    nspin = 2
    lijrms = 0
    for s in range(nspin):
        M = lambda_ij[s, :, :]
        e = (M - M.T)[np.triu_indices((M - M.T).shape[0])]
        e_tmp = 0.0
        for f in range(len(e)):
            e_tmp = e_tmp + e[f]**2.
        e_tmp = np.sqrt(e_tmp / (M.shape[0] * (M.shape[0] - 1)))
        lijrms = lijrms + e_tmp
    lijrms = lijrms / 2.
    return lijrms


def apply_field(mol, mf, E):
    #
    # add efield to hamiltonian
    #
    # The gauge origin for dipole integral
    mol.set_common_orig([0., 0., 0.])
    # recalculate h1e with extra efield
    h = (mol.intor('cint1e_kin_sph') + mol.intor('cint1e_nuc_sph') +
         np.einsum('x,xij->ij', E, mol.intor('cint1e_r_sph', comp=3)))
    # update h1e with efield
    mf.get_hcore = lambda *args: h


class PYFLOSIC(FileIOCalculator):
    """ PYFLOSIC calculator for atoms and molecules.
        by Sebastian Schwalbe
        Notes: ase.calculators -> units [eV,Angstroem,eV/Angstroem]
           pyflosic	   -> units [Ha,Bohr,Ha/Bohr]
    """
    implemented_properties = ['energy', 'forces', 'fodforces', 'evalues']
    PYFLOSIC_CMD = os.environ.get('ASE_PYFLOSIC_COMMAND')
    command = PYFLOSIC_CMD

    # Note: If you need to add keywords, please also add them in valid_args
    default_parameters = dict(
        atoms=None,           # ase atoms object nuclei
        fod1=None,            # ase atoms object FODs spin channel 1
        fod2=None,            # ase atoms objects FODs spin channnel 2
        mol=None,              # PySCF mole object
        charge=None,          # charge of the system
        spin=None,            # 2s = spin of the system
        basis=None,           # basis set
        ecp=None,             # only needed if ecp basis set is used
        xc='lda,pw',          # exchange correlation potential
        mode='flosic-os',     # calculation modus
        efield=None,            # applying a efield
        max_cycle=300,        # maximum scf cycles
        conv_tol=1e-5,        # energy threshold
        grid=3,               # numerical mesh
        ghost=False,           # ghost atoms at FOD positions
        mf=None,              # PySCF calculation object
        use_newton=False,       # use Newton scf cycle
        use_chk=False,          # restart from chk file
        verbose=0,              # output verbosity
        calc_forces=False,      # calculate FOD forces
        debug=False,            # extra ouput for debugging purpose
        l_ij=None,              # developer option: alternative optimization target
        ods=None,               # developer option: orbital damping sic
        fopt='force',           # developer option: in use with l_ij, alternative optimization target
        fixed_vsic=None,        # fixed SIC one body values Veff, Exc, Ecoul
        num_iter=0,             # scf iteration number
        vsic_every=1,           # calculate vsic after this number on num_iter cycles
        ham_sic='HOO'          # unified SIC Hamiltonian HOO or HOOOV
    )

    def __init__(self, restart=None, ignore_bad_restart_file=False,
                 label=os.curdir, atoms=None, **kwargs):
        """ Constructor """
        FileIOCalculator.__init__(self, restart, ignore_bad_restart_file,
                                  label, atoms, **kwargs)
        valid_args = (
            'atoms',
            'fod1',
            'fod2',
            'mol',
            'charge',
            'spin',
            'basis',
            'ecp',
            'xc',
            'mode',
            'efield',
            'max_cycle',
            'conv_tol',
            'grid',
            'ghost',
            'mf',
            'use_newton',
            'use_chk',
            'verbose',
            'calc_forces',
            'debug',
            'l_ij',
            'ods',
            'fopt',
            'fixed_vsic',
            'num_iter',
            'vsic_every',
            'ham_sic')
        # set any additional keyword arguments
        for arg, val in self.parameters.items():
            if arg in valid_args:
                setattr(self, arg, val)
            else:
                raise RuntimeError('unknown keyword arg "%s" : not in %s' % (arg, valid_args))
        self.results['fodforces'] = None
        self.set_atoms(atoms)

    def initialize(self, atoms=None, properties=['energy'], system_changes=['positions']):
        # Calculator.calculate(self,atoms,properties,system_changes)
        self.atoms = atoms

    def set_atoms(self, atoms):
        #self.atoms = copy.deepcopy(atoms)
        self.atoms = atoms

    def get_atoms(self):
        if self.atoms is None:
            raise ValueError('Calculator has no atoms')
        atoms = self.atoms.copy()
        atoms.calc = self
        return atoms
        # return FileIOCalculator.get_atoms(self)

    def set_label(self, label):
        self.label = label
        self.directory = label
        self.prefix = ''
        self.out = os.path.join(label, 'pyflosic.out')

    def check_state(self, atoms):
        system_changes = FileIOCalculator.check_state(self, atoms)
        # Ignore boundary conditions until now
        if 'pbc' in system_changes:
            system_changes.remove('pbc')
        return system_changes

    def set(self, **kwargs):
        changed_parameters = FileIOCalculator.set(self, **kwargs)
        if changed_parameters:
            self.reset()

    def write_input(self, atoms, properties=None, system_changes=None, **kwargs):
        FileIOCalculator.write_input(self, atoms, properties, system_changes)
        self.initialize(atoms)

    def get_energy(self):
        # get the energy from the results dict
        if self.calculation_required(self.atoms, 'energy'):
            self.calculate(self.atoms)
        if self.fopt == 'lij':
            res = force_max_lij(self.lambda_ij)
        if self.fopt == 'force':
            res = self.results['energy']
        if self.fopt == 'esic-force':
            res = self.results['esic']
        return res

    def get_forces(self, atoms=None):
        if atoms is not None:
            self.atoms = atoms
        # get nuclei and FOD forces
        # calculates forces if required
        if self.atoms is None:
            self.atoms = atoms
        # Note: The gradients for UKS are only available in the dev branch of pyscf.
        if self.mode == 'dft' or self.mode == 'both':
            from pyscf.grad import uks
            if self.mf is None:
                from pyscf import gto, scf, dft
                [geo, nuclei, fod1, fod2, included] = xyz_to_nuclei_fod(self.atoms)
                nuclei = ase2pyscf(nuclei)
                mol = gto.M(atom=nuclei, basis=self.basis, spin=self.spin, charge=self.charge)
                mf = scf.UKS(mol)
                if self.xc == 'LDA,PW' or self.xc == 'PBE,PBE':
                    # The 2nd order scf cycle (Newton) speed up calculations,
                    # tt but does not work for MGGAs like SCAN,SCAN.
                    mf = mf.as_scanner()
                    mf = mf.newton()
                mf.kernel()
                self.mf = mf
                gf = uks.Gradients(mf)
                forces = gf.kernel()
            # if self.mf != None:
            #	gf = uks.Gradients(self.mf)
            #        forces = gf.kernel()
            gf = uks.Gradients(self.mf)
            forces = gf.kernel()
            print(forces)

        if self.mode == 'flosic-os' or self.mode == 'flosic-scf':
            [geo, nuclei, fod1, fod2, included] = xyz_to_nuclei_fod(self.atoms)
            forces = np.zeros_like(nuclei.get_positions())

        if self.mode == 'dft':
            # mode for nuclei only optimization (fods fixed)
            forces = forces.tolist()
            totalforces = []
            totalforces.extend(forces)
            [geo, nuclei, fod1, fod2, included] = xyz_to_nuclei_fod(self.atoms)
            fod1forces = np.zeros_like(fod1.get_positions())
            fod2forces = np.zeros_like(fod2.get_positions())
            totalforces.extend(fod1forces)
            totalforces.extend(fod2forces)
            totalforces = np.array(totalforces)
            # pyscf gives the gradient not the force
            totalforces = -1 * totalforces

        if self.mode == 'flosic-os' or self.mode == 'flosic-scf':
            # mode for FOD only optimization (nuclei fixed)
            if self.results['fodforces'] is None:
                fodforces = self.get_fodforces(self.atoms)
            fodforces = self.results['fodforces']
            # fix nuclei with zeroing the forces
            forces = forces
            forces = forces.tolist()
            totalforces = []
            totalforces.extend(forces)
            totalforces.extend(fodforces)
            totalforces = np.array(totalforces)

        if self.mode == 'both':
            # mode for both (nuclei+fods) optimzation
            if self.results['fodforces'] is None:
                fodforces = self.get_fodforces(self.atoms)
            fodforces = self.results['fodforces']
            forces = forces.tolist()
            totalforces = []
            totalforces.extend(forces)
            totalforces.extend(fodforces)
            totalforces = np.array(totalforces)

        return totalforces

    def calculation_required(self, atoms, properties):
        # checks of some properties need to be calculated or not
        system_changes = self.check_state(atoms)
        if system_changes:
            return True
        for name in properties:
            if name not in self.results:
                return True
        return False

    def get_potential_energy(self, atoms, force_consistent=False):
        # calculate total energy if required
        if self.calculation_required(atoms, 'energy'):
            self.calculate(atoms)
        self.energy = self.results['energy']
        if self.fopt == 'lij':
            # res = force_max_lij(self.lambda_ij)
            res = self.results['energy']
        if self.fopt == 'force':
            res = self.results['energy']
        if self.fopt == 'esic-force':
            res = self.results['esic']
        return res

    def get_fodforces(self, atoms):
        self.atoms = atoms
        # FOD forces
        if self.calculation_required(atoms, 'fodforces'):
            self.get_potential_energy(atoms)
        self.fodforces = self.results['fodforces']
        return self.fodforces

    def get_dipole_moment(self):
        return self.results['dipole']

    def get_evalues(self):
        return self.results['evalues']

    def calculate(self, atoms, properties=['energy'], system_changes=['positions']):
        self.num_iter += 1
        atoms = self.get_atoms()
        self.atoms = atoms
        Calculator.calculate(self, atoms, properties, system_changes)
        if self.mode == 'dft':
            # DFT only mode
            from pyscf import gto, scf, grad, dft
            [geo, nuclei, fod1, fod2, included] = xyz_to_nuclei_fod(self.atoms)
            nuclei = ase2pyscf(nuclei)
            mol = gto.M(atom=nuclei, basis=self.basis, spin=self.spin, charge=self.charge)
            mf = scf.UKS(mol)
            # Verbosity of the mol object (o lowest output, 4 might enough output for debugging)
            mf.verbose = self.verbose
            e = mf.kernel()
            self.mf = mf
            self.results['energy'] = e * Ha
            self.results['dipole'] = dipole = mf.dip_moment()
            self.results['evalues'] = mf.mo_energy
        if self.mode == 'flosic-os':
            # FLOSIC SCF mode
            from pyscf import gto, scf
            [geo, nuclei, fod1, fod2, included] = xyz_to_nuclei_fod(self.atoms)
            # FLOSIC one shot mode
            #mf = flosic(self.atoms,charge=self.charge,spin=self.spin,xc=self.xc,basis=self.basis,debug=False,verbose=self.verbose)
            # Effective core potentials need so special treatment.
            if self.ecp is None:
                if not self.ghost:
                    mol = gto.M(atom=ase2pyscf(nuclei), basis=self.basis, spin=self.spin, charge=self.charge)
                if self.ghost:
                    mol = gto.M(atom=ase2pyscf(nuclei), basis=self.basis, spin=self.spin, charge=self.charge)
                    mol.basis = {
                        'default': self.basis, 'GHOST1': gto.basis.load(
                            'sto3g', 'H'), 'GHOST2': gto.basis.load(
                            'sto3g', 'H')}
            if self.ecp is not None:
                mol = gto.M(atom=ase2pyscf(nuclei), basis=self.basis, spin=self.spin, charge=self.charge, ecp=self.ecp)
            mf = scf.UKS(mol)
            mf.xc = self.xc
            # Verbosity of the mol object (o lowest output, 4 might enough output for debugging)
            mf.verbose = self.verbose
            # Binary output format of pyscf.
            # Save MOs, orbital energies, etc.
            if self.use_chk and not self.use_newton:
                mf.chkfile = 'pyflosic.chk'
            # Load from previous run, if exist, the checkfile.
            # Hopefully this will speed up the calculation.
            if self.use_chk and not self.use_newton and os.path.isfile('pyflosic.chk'):
                mf.init_guess = 'chk'
                mf.update('pyflosic.chk')
            if self.use_newton:
                mf = mf.as_scanner()
                mf = mf.newton()
            mf.max_cycle = self.max_cycle
            mf.conv_tol = self.conv_tol
            mf.grids.level = self.grid
            e = mf.kernel()
            self.mf = mf
            mf = flosic(
                mol,
                mf,
                fod1,
                fod2,
                sysname=None,
                datatype=np.float64,
                print_dm_one=False,
                print_dm_all=False,
                debug=self.debug,
                calc_forces=True)
            self.results['energy'] = mf['etot_sic'] * Ha
            # unit conversion from Ha/Bohr to eV/Ang
            #self.results['fodforces'] = -1*mf['fforces']/(Ha/Bohr)
            self.results['fodforces'] = -1 * mf['fforces'] * (Ha / Bohr)
            print('Analytical FOD force [Ha/Bohr]')
            print(mf['fforces'])
            print('fmax = %0.6f [Ha/Bohr]' % np.sqrt((mf['fforces']**2).sum(axis=1).max()))
            self.results['dipole'] = mf['dipole']
            self.results['evalues'] = mf['evalues']
        if self.mode == 'flosic-scf':
            if self.mf is None:
                # FLOSIC SCF mode
                from pyscf import gto
                [geo, nuclei, fod1, fod2, included] = xyz_to_nuclei_fod(self.atoms)
                # Effective core potentials need so special treatment.
                if self.ecp is None:
                    if not self.ghost:
                        mol = gto.M(atom=ase2pyscf(nuclei), basis=self.basis, spin=self.spin, charge=self.charge)
                    if self.ghost:
                        mol = gto.M(atom=ase2pyscf(nuclei), basis=self.basis, spin=self.spin, charge=self.charge)
                        mol.basis = {
                            'default': self.basis, 'GHOST1': gto.basis.load(
                                'sto3g', 'H'), 'GHOST2': gto.basis.load(
                                'sto3g', 'H')}
                if self.ecp is not None:
                    mol = gto.M(
                        atom=ase2pyscf(nuclei),
                        basis=self.basis,
                        spin=self.spin,
                        charge=self.charge,
                        ecp=self.ecp)
                if self.efield is not None:
                    m0 = FLOSIC(
                        mol=mol,
                        xc=self.xc,
                        fod1=fod1,
                        fod2=fod2,
                        grid_level=self.grid,
                        debug=self.debug,
                        l_ij=self.l_ij,
                        ods=self.ods,
                        fixed_vsic=self.fixed_vsic,
                        num_iter=self.num_iter,
                        vsic_every=self.vsic_every,
                        ham_sic=self.ham_sic)
                    # test efield to enforce some pseudo chemical environment
                    # and break symmetry of density
                    m0.grids.level = self.grid
                    m0.conv_tol = self.conv_tol
                    # small efield
                    m0.max_cycle = 1
                    h = -0.0001  # -0.1
                    apply_field(mol, m0, E=(0, 0, 0 + h))
                    m0.kernel()
                mf = FLOSIC(
                    mol=mol,
                    xc=self.xc,
                    fod1=fod1,
                    fod2=fod2,
                    grid_level=self.grid,
                    calc_forces=self.calc_forces,
                    debug=self.debug,
                    l_ij=self.l_ij,
                    ods=self.ods,
                    fixed_vsic=self.fixed_vsic,
                    num_iter=self.num_iter,
                    vsic_every=self.vsic_every,
                    ham_sic=self.ham_sic)
                # Verbosity of the mol object (o lowest output, 4 might enough output for debugging)
                mf.verbose = self.verbose
                # Binary output format of pyscf.
                # Save MOs, orbital energies, etc.
                if self.use_chk and not self.use_newton:
                    mf.chkfile = 'pyflosic.chk'
                # Load from previous run, if exist, the checkfile.
                # Hopefully this will speed up the calculation.
                if self.use_chk and not self.use_newton and os.path.isfile('pyflosic.chk'):
                    mf.init_guess = 'chk'
                    mf.update('pyflosic.chk')
                if self.use_newton:
                    mf = mf.as_scanner()
                    mf = mf.newton()
                mf.max_cycle = self.max_cycle
                mf.conv_tol = self.conv_tol
                mf.grids.level = self.grid
                e = mf.kernel()
                self.mf = mf
                # Return some results to the pyflosic_ase_caculator object.
                self.results['esic'] = mf.esic * Ha
                self.results['energy'] = e * Ha
                self.results['fixed_vsic'] = mf.fixed_vsic
            if self.mf is not None:
                from pyscf import gto
                [geo, nuclei, fod1, fod2, included] = xyz_to_nuclei_fod(self.atoms)
                # Effective core potentials need so special treatment.
                if self.ecp is None:
                    if not self.ghost:
                        mol = gto.M(atom=ase2pyscf(nuclei), basis=self.basis, spin=self.spin, charge=self.charge)
                    if self.ghost:
                        mol = gto.M(atom=ase2pyscf(nuclei), basis=self.basis, spin=self.spin, charge=self.charge)
                        mol.basis = {
                            'default': self.basis, 'GHOST1': gto.basis.load(
                                'sto3g', 'H'), 'GHOST2': gto.basis.load(
                                'sto3g', 'H')}
                if self.ecp is not None:
                    mol = gto.M(
                        atom=ase2pyscf(nuclei),
                        basis=self.basis,
                        spin=self.spin,
                        charge=self.charge,
                        ecp=self.ecp)
                self.mf.num_iter = self.num_iter
                self.mf.max_cycle = self.max_cycle
                self.mf.mol = mol
                self.mf.fod1 = fod1
                self.mf.fod2 = fod2
                e = self.mf.kernel()
                # Return some results to the pyflosic_ase_caculator object.
                self.results['esic'] = self.mf.esic * Ha
                self.results['energy'] = e * Ha
                self.results['fixed_vsic'] = self.mf.fixed_vsic

            if self.fopt == 'force' or self.fopt == 'esic-force':
                #
                # The standard optimization uses
                # the analytical FOD forces
                #
                fforces = self.mf.get_fforces()
                #fforces = -1*fforce
                # unit conversion Hartree/Bohr to eV/Angstroem
                self.results['fodforces'] = -1 * fforces * (Ha / Bohr)
                print('Analytical FOD force [Ha/Bohr]')
                print(fforces)
                print('fmax = %0.6f [Ha/Bohr]' % np.sqrt((fforces**2).sum(axis=1).max()))

            if self.fopt == 'lij':
                #
                # This is under development.
                # Trying to replace the FOD forces.
                #
                self.lambda_ij = self.mf.lambda_ij
                self.results['lambda_ij'] = self.mf.lambda_ij
                #fforces = []
                #nspin = 2
                # for s in range(nspin):
                #	# printing the lampda_ij matrix for both spin channels
                #	print 'lambda_ij'
                #	print lambda_ij[s,:,:]
                #	print 'RMS lambda_ij'
                #	M = lambda_ij[s,:,:]
                #	fforces_tmp =  (M-M.T)[np.triu_indices((M-M.T).shape[0])]
                #	fforces.append(fforces_tmp.tolist())
                # print np.array(fforces).shape
                try:
                    #
                    # Try to calculate the FOD forces from the differences
                    # of SIC eigenvalues
                    #
                    evalues_old = self.results['evalues']
                    print(evalues_old)
                    evalues_new = self.mf.evalues
                    print(evalues_new)
                    delta_evalues_up = (evalues_old[0][0:len(fod1)] - evalues_new[0][0:len(fod1)]).tolist()
                    delta_evalues_dn = (evalues_old[1][0:len(fod2)] - evalues_new[1][0:len(fod2)]).tolist()
                    print(delta_evalues_up)
                    print(delta_evalues_dn)
                    lij_force = delta_evalues_up
                    lij_force.append(delta_evalues_dn)
                    lij_force = np.array(lij_force)
                    lij_force = np.array(lij_force, (np.shape(lij_force)[0], 3))
                    print('FOD force evalued from evalues')
                    print(lij_force)
                    self.results['fodforces'] = lij_force
                except BaseException:
                    #
                    # If we are in the first iteration
                    # we can still use the analystical FOD forces
                    # as starting values
                    #
                    fforces = self.mf.get_fforces()
                    print(fforces)
                    #self.results['fodforces'] = -1*fforces*(Ha/Bohr)
                    self.results['fodforces'] = -1 * fforces * (Ha / Bohr)
                    print('Analytical FOD force [Ha/Bohr]')
                    print(fforces)
                    print('fmax = %0.6f [Ha/Bohr]' % np.sqrt((fforces**2).sum(axis=1).max()))

            self.results['dipole'] = self.mf.dip_moment()
            self.results['evalues'] = self.mf.evalues

        if atoms is not None:
            self.atoms = atoms.copy()


if __name__ == "__main__":
    from ase.io import read
    import os

    # Path to the xyz file
    f_xyz = os.path.dirname(os.path.realpath(__file__)) + '/../examples/ase_pyflosic_optimizer/LiH.xyz'
    atoms = read(f_xyz)
    calc = PYFLOSIC(atoms=atoms, charge=0, spin=0, xc='LDA,PW', basis='cc-pvqz')
    print('Pyflosic total energy: ', calc.get_energy())
    print('Pyflosic total forces: ', calc.get_forces())
