import sys
import os
from enum import Enum
import tomllib

colors = [
        "#700ea4",
        "#ac7a0e",
        "#1999b3",
        "#1f93d2",
        "#a5378b",
        "#a22385",
        "#1fb4b4",
        "#d14d0f",
        "#348cc3",
        "#6e6215",
        "#d45030",
        "#9a2f27",
        "#384f18",
        "#157b81",
        "#9d611e"
    ]


class Mode(Enum):
    Mermaid = 0
    Count = 1
    Colours = 2


def find_path(directory):
    # Find all .toml files in the directory recursively
    modules = {}
    dependencies = 0
    for root, dirs, files in os.walk(directory):
        # print(f"Looking in {directory}")
        for file in files:
            if file.endswith('Cargo.toml'):
                mod = []
                mod_name = root.split('/')[-1]
                print(f"********** {mod_name} *************")
                try:
                    with open(os.path.join(root, file), 'rb') as tomlstream:
                        cargo = tomllib.load(tomlstream)
                        for section, section_data in cargo.items():
                            if section.startswith("dependencies"):
                                for dep, dep_values in section_data.items():

                                    if "path" in dep_values:
                                        print(section, dep, dep_values)
                                        mod.append(dep.replace("_", "-"))
                                        dependencies += 1
                except ValueError as error:
                    print(f"Could not parse {root}")
                    print(error)

                if mod_name in modules:
                    modules[mod_name].extend(mod["dependencies"])
                else:
                    modules[mod_name] = mod
    print(f"Found {len(modules)} Modules")
    print(f"Found {dependencies} Dependencies")

    return modules


def map_paths(paths):

    modules = {}
    for p in paths:
        mods = find_path(p)
        for m, d in mods.items():
            if m not in modules:
                modules[m] = d
            else:
                modules[m] = set(modules[m] + d)

    mod_counts = {}

    for mod, deps in modules.items():
        if mod not in mod_counts:
            mod_counts[mod] = 0

        for d in deps:
            if d not in mod_counts:
                mod_counts[d] = 0
            mod_counts[d] += 1
    top_levels = []
    for mod, counts in mod_counts.items():
        if counts == 0:
            print(f"{mod} is a top level module")
            top_levels.append(mod)

    mode = Mode.Colours

    match mode:
        case Mode.Mermaid:
            # generate graph
            print("```")
            print("flowchart")
            for mod, deps in modules.items():
                print(f"\t{mod}")
            for mod, deps in modules.items():
                for d in deps:
                    print(f"\t{mod} --> {d}")
            print("```")
        case Mode.Count:
            # List counts
            for mod, deps in modules.items():
                print(f"Mod: {mod}\tCount: {len(deps)}")
        case Mode.Colours:
            index = 0
            line = 0
            print("```")
            print("flowchart")
            for mod, deps in modules.items():
                print(f"\t{mod}:::class{mod}")
            for mod, deps in modules.items():
                for d in deps:
                    print(f"\t{mod} --> {d}")

            for mod, deps in modules.items():
                c = colors[index]
                print(f"classDef class{mod} stroke:{c}")
                for d in deps:
                    print(f"linkStyle {line} stroke-width:2px,stroke:{c}")
                    line += 1
                index += 1
            print("```")


if __name__ == "__main__":
    map_paths(sys.argv[1:])

# python mapper.py /Users/jon/Programming/ensembl-dauphin-style-compiler
# /Users/jon/Programming/peregrine-eachorevery
# /Users/jon/Programming/peregrine-eard
