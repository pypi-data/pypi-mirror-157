import json
import os.path
from typing import List, Tuple


def dist(p1, p2):
    return sum([(p1[0] - p2[0]) ** 2, (p1[1] - p2[1]) ** 2, (p1[2] - p2[2]) ** 2]) ** (1 / 2)


class Residue:
    """Residue class"""

    def __init__(self, line: str) -> None:
        """

        :param line:
        """
        self.name = line[17:20].strip()
        self.num = int(line[22:26].strip())
        self.x = float(line[30:38].strip())
        self.y = float(line[38:46].strip())
        self.z = float(line[46:54].strip())


class PDBStructure:
    """Structure class"""

    def __init__(self, filename: str) -> None:
        """

        :param filename:
        """
        self.residues = {}
        with open(filename, "r") as in_file:
            for line in in_file.readlines():
                if line.startswith("ATOM") and line[12:16].strip() == "CA":
                    res = Residue(line)
                    self.residues[res.num] = res

    def __len__(self) -> int:
        """

        :return:
        """
        return len(self.residues)

    def __get_coords(self) -> List[Tuple[int, int, int]]:
        """

        :return:
        """
        coords = [[res.x, res.y, res.z] for res in self.residues.values()]
        return coords

    def __get_edges(self, threshold: float):
        """
        Get edges of a graph using threshold as a cutoff

        :param threshold:
        :return:
        """
        coords = self.__get_coords()
        edges = [(i, j) for i in range(len(coords)) for j in range(len(coords)) if
                 i < j and dist(coords[i], coords[j]) < threshold]
        return list(zip(*edges))

    def store_graph(self, output_file: str, activities: List[float], distances: List[float], threshold: float):
        """

        :param output_file:
        :param activities:
        :param threshold:
        :return:
        """
        edges = self.__get_edges(threshold)
        positions = self.__get_coords()
        names = [f"{i}_{res.name}" for i, res in enumerate(self.residues.values())]
        output = {
            "nodes": [{
                "name": names[i],
                "x": positions[i][0],
                "y": positions[i][1],
                "z": positions[i][2],
                "activity": str(activities[i]),
                "distance": str(distances[i]),
            } for i in range(len(self.residues))],
            "edges": {
                "start": edges[0],
                "end": edges[1],
            },
        }
        json.dump(output, open(output_file, "w"))


def view(
        pdb_file: str,
        output_dir: str,
        activities: List[float],
        distances: List[float],
        threshold: float = 4.0
    ) -> None:
    """
    Generate the json output file storing the protein structure and the activities per residue to be displayed in the
    web interface.

    :param pdb_file: Input file of the protein defining its structure
    :param output_dir: Output directory to store the json file in
    :param activities: List of the activities from a model. This should have as many entries as the PDB file contains
        residues.
    :param distances: List of the distances between each residue and a ligand in the binding pocket. This should have
        as many entries as the PDB file contains residues.
    :param threshold:

    :return: Nothing
    """
    if not os.path.exists(pdb_file):
        raise ValueError("PDB-File does not exist!")
    if not os.path.exists(output_dir):
        raise ValueError("Output directory does not exist!")

    struct = PDBStructure(pdb_file)

    if len(struct) != len(activities):
        raise ValueError("PDB-File has more residues then the activity-list entries!")

    struct.store_graph(os.path.join(output_dir, os.path.splitext(os.path.basename(pdb_file))[0] + ".json"),
                       activities, distances, threshold)
