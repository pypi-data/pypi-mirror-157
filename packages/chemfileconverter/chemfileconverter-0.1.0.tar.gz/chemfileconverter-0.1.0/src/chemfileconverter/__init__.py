__version__ = '0.1.0'

from typing import IO
from typing import Any
from typing import TextIO


def load(fp: TextIO) -> Any:
    """Deserialize ``fp`` (a ``.read()``-supporting file-like object containing
    a Chemical Table document) to a Python object.
    """
    return loads(fp.read())


def loads(s):
    """Deserialize ``s`` (a ``str`` instance
    containing a Chemical Table document) to a Python object.
    """
    return ChemDecoder().decode(s)


class ChemDecoder():
    def __init__(self):
        pass

    def decode(self, s):
        """Return the Python representation of ``s`` (a ``str`` instance
        containing a Chemical Table document).
        """
        obj = {}
        content = s.split('\n')

        obj.setdefault('name', content[2].split()[1])
        obj.setdefault('program', content[2].split()[0])

        obj.setdefault('substrate_count', int(content[4].split()[0]))
        obj.setdefault('product_count', int(content[4].split()[1]))
        metabolite_count = int(content[4].split()[0]) + int(content[4].split()[1])
        mol_files = self._read_molfiles(content, metabolite_count)
        obj.setdefault('mol_files', mol_files)

        return obj

    def _read_molfiles(self, s: str, metabolite_count: int):
        mol_files = []

        mol_indices = [i for i in range(len(s)) if s[i] == '$MOL']
        if len(mol_indices) != metabolite_count:
            raise ValueError('Metabolites do not match the substrate and product counts')

        for index in range(len(mol_indices)):
            mol_file = {}
            try:
                mol = s[mol_indices[index]:mol_indices[index + 1]]
            except IndexError:
                mol = s[mol_indices[index]:]

            mol_file.setdefault('name', mol[1])
            mol_file.setdefault('program', mol[2])
            mol_file.setdefault('comment', mol[3])
            mol_file.setdefault('index', index)

            # Count Line
            counts_line = mol[4].split()
            mol_file.setdefault('counts_line', {})
            mol_file['counts_line'].setdefault('atom_count',
                                               int(counts_line[0]))
            mol_file['counts_line'].setdefault('bond_count',
                                               int(counts_line[1]))
            mol_file['counts_line'].setdefault('atom_list_number',
                                               int(counts_line[2]))
            mol_file['counts_line'].setdefault('chiral_flag',
                                               int(counts_line[4]))
            mol_file['counts_line'].setdefault('stext_entries',
                                               int(counts_line[5]))
            mol_file['counts_line'].setdefault('additional_properties',
                                               int(counts_line[9]))
            mol_file['counts_line'].setdefault('version',
                                               counts_line[10])

            # Atom Block
            atom_count = mol_file['counts_line']['atom_count']
            atom_block = mol[5:atom_count + 5]
            mol_file.setdefault('atom_block', [])

            for index_atom, atom in enumerate(atom_block):
                atom_dict = {}

                atom_dict.setdefault('id', index_atom + 1)
                atom_dict.setdefault('x', float(atom[0:10]))
                atom_dict.setdefault('y', float(atom[10:20]))
                atom_dict.setdefault('z', float(atom[20:30]))
                atom_dict.setdefault('symbol', atom[30:33].strip())
                atom_dict.setdefault('mass_difference', float(atom[33:36]))
                atom_dict.setdefault('charge', int(atom[36:39]))
                atom_dict.setdefault('stereo_parity', int(atom[39:42]))
                atom_dict.setdefault('hydrogen_count', int(atom[42:45]))
                atom_dict.setdefault('stereo_care', int(atom[45:48]))
                atom_dict.setdefault('valence', int(atom[48:51]))
                atom_dict.setdefault('h0_designator', int(atom[51:54]))
                atom_dict.setdefault('aam', atom[60:63].strip())
                atom_dict.setdefault('inversion_retention_flag',
                                     int(atom[63:66]))
                atom_dict.setdefault('exact_change_flag',
                                     int(atom[66:69]))
                mol_file['atom_block'].append(atom_dict)

            # Bond Block
            bond_count = mol_file['counts_line']['bond_count']
            atom_end = atom_count + 5
            bond_block = mol[atom_end:atom_end + bond_count]
            mol_file.setdefault('bond_block', [])

            if bond_block:
                for index_bond, bond in enumerate(bond_block):
                    bond_dict = {}

                    bond_dict.setdefault('id', index_bond + 1)
                    bond_dict.setdefault('first_atom', int(bond[0:3]))
                    bond_dict.setdefault('second_atom', int(bond[3:6]))
                    bond_dict.setdefault('bond_type', int(bond[6:9]))
                    bond_dict.setdefault('bond_stereo', int(bond[9:12]))
                    bond_dict.setdefault('bond_topology', int(bond[12:15]))
                    bond_dict.setdefault('reaction_center', int(bond[15:18]))

                    mol_file['bond_block'].append(bond_dict)

            # Properties Block
            properties_block = mol[atom_end + bond_count:]
            properties = []
            for prop_index in range(len(properties_block)):
                if properties_block[prop_index] == 'M  END' or not properties_block[prop_index]:
                    continue
                properties.append(properties_block[prop_index])

            mol_file.setdefault('properties_block', properties)

            mol_files.append(mol_file)

        return mol_files


def dump(obj: Any, fp: IO[str]) -> None:
    s = dumps(obj)
    fp.write(s)


def dumps(obj: Any) -> str:
    s = '$RXN\n\n'
    s += f'  {obj["program"]}     {obj["name"]}\n\n'
    substrate_whitespace = ' '*(3-len(str(obj["substrate_count"])))
    product_whitespace = ' '*(3-len(str(obj["product_count"])))
    s += f'{substrate_whitespace}{obj["substrate_count"]}{product_whitespace}{obj["product_count"]}\n'
    for mol in obj['mol_files']:
        s += f'$MOL\n{mol["name"]}\n{mol["program"]}\n{mol["comment"]}\n'

        counts_line = ''
        for key, value in mol['counts_line'].items():
            if key == 'version':
                white_space = ' '
            else:
                white_space = ' '*(3-len(str(value)))
            counts_line += f'{white_space}{value}'
        counts_line += '\n'
        s += counts_line

        atom_block = ''
        for entry in mol['atom_block']:
            for key, value in entry.items():
                if key in ['x', 'y', 'z']:
                    white_space = ' '*(10-len(str(value)))
                    atom_block += f'{white_space}{value}'
                elif key == 'symbol':
                    white_space = ' '
                    white_space_after = ' '*(2-len(str(value)))
                    atom_block += f'{white_space}{value}{white_space_after}'
                elif key == 'id':
                    continue
                else:
                    white_space = ' '*(3-len(str(value)))
                    atom_block += f'{white_space}{value}'
            atom_block += '\n'
        s += atom_block

        bond_block = ''
        for entry in mol['bond_block']:
            for key, value in entry.items():
                if key == 'id':
                    continue
                white_space = ' '*(3-len(str(value)))
                bond_block += f'{white_space}{value}'
            bond_block += '\n'
        s += bond_block

        properties_block = ''
        for entry in mol['properties_block']:
            properties_block += entry
            properties_block += '\n'

        s += 'M END\n'

    return s
