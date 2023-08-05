from ctypes import c_int, c_double, c_float, c_char, addressof, memmove, sizeof

from delphi4py.readFiles import readFiles as readF
from delphi4py.rundelphi import rundelphi as DelPhi
import delphi4py.defaults as defaults

# if using parallel version don't forget to set system-wide variables
# export OMP_NUM_THREADS=8
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/pedror/delphit/dependencies/NanoShaper0.7/build_lib:/home/pedror/delphit/dependencies/cppDelphi77/lib/


class DelPhi4py:
    """Wrapper class for DelPhi."""

    def __init__(self, in_crg, in_siz, in_pdb, **kwargs):
        # TODO: extend number of input parameters to include all/most DelPhi input parameters

        self.in_crg = str(in_crg)
        self.in_siz = str(in_siz)
        self.in_pdb = str(in_pdb)

        for param, defaultval in defaults.__dict__.items():
            if param in kwargs:
                self[param] = kwargs[param]
            else:
                self[param] = defaultval

        self.natoms = int(self.get_total_atoms())

        self.in_crg_len = len(self.in_crg)
        self.in_siz_len = len(self.in_siz)
        self.in_pdb_len = len(self.in_pdb)

        self.scale_prefocus = float(self.scale)

        if self.precision == "double":
            self.float_type = c_double
        elif self.precision == "single":
            self.float_type = c_float
        else:
            raise IOError(
                "Unknown precision definition {0}. "
                'It should be either "double" or "single"'.format(self.precision)
            )

        # -1 NanoShaper off     0 connolly surface     1 skin
        #  2 blobby             3 mesh                 4 msms
        # only tested -1 and 0
        if self.isurftype not in (0, -1):
            raise IOError(
                "Unknown precision definition {0}. "
                "It should be either 0 to activate or -1 to deactivate".format(
                    self.isurftype
                )
            )

        self.resetDelPhiData()
        self.readFiles()

        if self.perfil != 0:
            self.get_pdb_dims()
            self.igrid = int(self.scale * 100 / self.perfil * self.rmaxdim)
            self.igrid_focus = self.igrid

        if self.igrid % 2 == 0:
            self.igrid += 1

        self.esolvation = 999.999

    def get_pdb_dims(self):
        xs, ys, zs = [], [], []
        with open(self.in_pdb) as f:
            for line in f:
                if line.startswith("ATOM"):
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    xs.append(x)
                    ys.append(y)
                    zs.append(z)
        x_size = max(xs) - min(xs)
        y_size = max(ys) - min(ys)
        z_size = max(zs) - min(zs)
        self.rmaxdim = max((x_size, y_size, z_size))

    def get_total_atoms(self):
        c = 0
        with open(self.in_pdb) as f:
            for line in f:
                if line.startswith("ATOM "):
                    c += 1
        return c

    def resetDelPhiData(self):
        """Resets all DelPhi Input data structures"""
        # internal DelPhi DataStructures
        # defined as c_type arrays and
        # passed to DelPhi as pointers
        self.atpos = self.float_type * 3 * self.natoms
        self.p_atpos = self.atpos()
        self.i_atpos = addressof(self.p_atpos)

        self.rad3 = self.float_type * self.natoms
        self.p_rad3 = self.rad3()
        self.i_rad3 = addressof(self.p_rad3)

        self.chrgv4 = self.float_type * self.natoms
        self.p_chrgv4 = self.chrgv4()
        self.i_chrgv4 = addressof(self.p_chrgv4)

        self.atinf = (c_char * 15 * self.natoms)()
        self.i_atinf = addressof(self.atinf)

        self.nmedia = 1
        self.nobject = 1
        self.len_medeps = self.nmedia + self.nobject
        self.medeps = self.float_type * self.len_medeps
        self.p_medeps = self.medeps()
        self.i_medeps = addressof(self.p_medeps)

        self.len_iatmed = self.natoms + 1
        self.iatmed = c_int * self.len_iatmed
        self.p_iatmed = self.iatmed()
        self.i_iatmmed = addressof(self.p_iatmed)

        self.dataobject = (c_char * 96 * self.nobject * 2)()
        self.i_dataobject = addressof(self.dataobject)

    def changeStructureSize(
        self, p_atpos, p_rad3, p_chrgv4, atinf, p_iatmed, extra_atoms=None, natoms=None
    ):

        if not extra_atoms:
            extra_atoms = []

        if not natoms:
            natoms = self.natoms

        self.natoms = natoms + len(extra_atoms)

        self.atpos = self.float_type * 3 * self.natoms
        self.p_atpos = self.atpos()
        self.i_atpos = addressof(self.p_atpos)
        memmove(
            self.i_atpos, addressof(p_atpos), sizeof(self.float_type) * 3 * self.natoms
        )

        self.rad3 = self.float_type * self.natoms
        self.p_rad3 = self.rad3()
        self.i_rad3 = addressof(self.p_rad3)
        memmove(self.i_rad3, addressof(p_rad3), sizeof(self.float_type) * self.natoms)

        self.chrgv4 = self.float_type * self.natoms
        self.p_chrgv4 = self.chrgv4()
        self.i_chrgv4 = addressof(self.p_chrgv4)
        memmove(
            self.i_chrgv4, addressof(p_chrgv4), sizeof(self.float_type) * self.natoms
        )

        self.atinf = (c_char * 15 * self.natoms)()
        self.i_atinf = addressof(self.atinf)
        memmove(self.i_atinf, addressof(atinf), sizeof(c_char) * 15 * self.natoms)

        self.len_iatmed = self.natoms + 1
        self.iatmed = c_int * self.len_iatmed
        self.p_iatmed = self.iatmed()
        self.i_iatmmed = addressof(self.p_iatmed)
        memmove(self.i_iatmmed, addressof(p_iatmed), sizeof(c_int) * self.len_iatmed)

        atom_index = natoms - 1
        for atom in extra_atoms:
            atom_index += 1
            self.p_atpos[atom_index][0] = atom[0]
            self.p_atpos[atom_index][1] = atom[1]
            self.p_atpos[atom_index][2] = atom[2]
            self.p_rad3[atom_index] = atom[3]
            self.p_chrgv4[atom_index] = atom[4]
            self.atinf[atom_index].value = atom[5]
            self.p_iatmed[atom_index + 1] = 1

        return self.natoms

    def get_atpos(self):
        return self.p_atpos

    def get_rad3(self):
        return self.p_rad3

    def get_chrgv4(self):
        return self.p_chrgv4

    def get_atinf(self):
        return self.atinf

    def get_iatmed(self):
        return self.p_iatmed

    def readFiles(self):
        """ """
        readF.delphi(
            self.igrid,
            self.scale,
            self.epsin,
            self.epsout,
            self.acent,
            self.in_pdb,
            self.in_crg,
            self.in_siz,
            self.natoms,
            self.nobject,
            self.i_atpos,
            self.i_rad3,
            self.i_chrgv4,
            self.i_atinf,
            self.i_medeps,
            self.i_iatmmed,
            self.i_dataobject,
            self.rmaxdim,
            self.outputfile,
        )

        if self.debug:
            print("    x        y        z     radius  charge       atinf")
            for i in range(self.natoms):
                print(
                    (
                        "{0:8.3f} {1:8.3f} {2:8.3f} {3:7.3f} {4:7.3f} {5}".format(
                            self.p_atpos[i][0],
                            self.p_atpos[i][1],
                            self.p_atpos[i][2],
                            self.p_rad3[i],
                            self.p_chrgv4[i],
                            self.atinf[i].value,
                        )
                    )
                )

    def runDelPhi(
        self, in_frc="", out_phi=False, filename=None, outputfile="/dev/null", **kwargs
    ):
        for key, value in kwargs.items():
            if key in self.__dict__:
                self[key] = value
            else:
                raise Exception(f"Argument {key} is not valid.")

        if in_frc != "self":
            self.len_phimap = 0
        else:
            self.len_phimap = self.igrid * self.igrid * self.igrid

        if self.ibctyp != 3:
            self.phimap4 = c_float * self.len_phimap
            self.p_phimap4 = self.phimap4()
            self.i_phimap4 = addressof(self.p_phimap4)

            # Erase Site Potential
            self.sitpot = self.float_type * self.natoms
            self.p_sitpot = self.sitpot()
            self.i_sitpot = addressof(self.p_sitpot)
            self.p_sitpot_list = []

        if self.debug:
            output = self.__str__()
            print(output)
            if filename:
                with open(filename, "a") as f_new:
                    f_new.write(output)

        self.esolvation = DelPhi.delphi(
            self.igrid,
            self.scale,
            self.epsin,
            self.epsout,
            self.radprb,
            self.conc,
            self.ibctyp,
            self.res2,
            self.nlit,
            self.acent,
            self.energy,
            self.site,
            self.nonit,
            self.relfac,
            self.relpar,
            self.pbx,
            self.pby,
            in_frc,
            self.natoms,
            self.nmedia,
            self.nobject,
            self.i_atpos,
            self.i_rad3,
            self.i_chrgv4,
            self.i_atinf,
            self.i_medeps,
            self.i_iatmmed,
            self.i_dataobject,
            self.i_phimap4,
            self.scale_prefocus,
            out_phi,
            self.i_sitpot,
            self.esolvation,
            self.isurftype,
            self.parallel,
            outputfile,
        )
        self.saveSitePotential()

    def runFocusing(self, ibctyp, acent, k, params=None):
        for step in range(k + 1):
            in_frc = "self"
            if step == k:
                out_phi = False
            else:
                out_phi = True

            if step != 0:
                ibctyp = 3

            self.runDelPhi(
                **params[step],
                acent=acent,
                ibctyp=ibctyp,
                in_frc=in_frc,
                out_phi=out_phi,
            )

    def getSolvation(self):
        return self.esolvation

    def getSitePotential(self):
        """Returns site potential as a python list"""
        return self.p_sitpot_list

    def saveSitePotential(self):
        """"""
        p_sitpot_list = []
        # if focus is being done update new values
        if len(self.p_sitpot_list) > 0:
            for i in range(len(self.p_sitpot)):
                val = self.p_sitpot[i]
                if val != 0.0:
                    p_sitpot_list.append(val)
                else:
                    p_sitpot_list.append(self.p_sitpot_list[i])
        else:
            for i in self.p_sitpot:
                p_sitpot_list.append(i)

        self.p_sitpot_list = p_sitpot_list

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __str__(self):
        """Outputs the parameters used"""
        out = """
        DelPhi Parameters

        igrid       = {}
        scale       = {}
        perfil      = {}

        epsin  = {}
        epsout = {}
        conc    = {}
        ibctyp  = {}
        res2    = {}
        nlit    = {}

        acent  = {}
        natoms = {}
        in_crg = {}
        in_siz = {}
        in_pdb = {}

        radprb  = {}
        energy  = {}
        site    = {}
        in_crg_len = {}
        in_siz_len = {}
        in_pdb_len = {}

        relfac = {}
        relpar = {}
        nonit  = {}
        fcrg   = {}
        pbx    = {}
        pby    = {}

        precision  = {}
        float_type = {}
        isurftype  = {}
        parallel   = {}
        debug      = {}

        """.format(
            self.igrid,
            self.scale,
            self.perfil,
            self.epsin,
            self.epsout,
            self.conc,
            self.ibctyp,
            self.res2,
            self.nlit,
            self.acent,
            self.natoms,
            self.in_crg,
            self.in_siz,
            self.in_pdb,
            self.radprb,
            self.energy,
            self.site,
            self.in_crg_len,
            self.in_siz_len,
            self.in_pdb_len,
            self.relfac,
            self.relpar,
            self.nonit,
            self.fcrg,
            self.pbx,
            self.pby,
            self.precision,
            self.float_type,
            self.isurftype,
            self.parallel,
            self.debug,
        )
        return out
