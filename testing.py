import copy
import gc
import os
from typing import List

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.legend_handler import HandlerTuple
from matplotlib.patches import Patch
from graphviz import Graph, Digraph


# inp = "../../Conferences and Papers/2023 CIBCB/AAMatcher/AAMOut/"
inp = "./AAMTestOut/"
outp = "./AAMTestFigs/"
finame1 = "crossover01_start.dat"
finame2 = "crossover01_end.dat"
samps = 200  # 2 for each 100 tests
precision = 6
col_width = 8 + precision


def process_readme(filename: str):
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            if line.__contains__("States"):
                sda_states = int(line.rstrip().split(":")[1].strip())
                pass
            if line.__contains__("Alphabet"):
                sda_chars = int(line.rstrip().split(":")[1].strip())
                pass
            if line.__contains__("Population"):
                popsize = int(line.rstrip().split(":")[1].strip())
                pass
            if line.__contains__("Crossover Operator"):
                crossOp = str(line.rstrip().split(":")[1].strip())
                pass
            if line.__contains__("Maximum Number of Mutations"):
                maxMuts = int(line.rstrip().split(":")[1].strip())
                pass
            pass
        pass
    return popsize, sda_states, sda_chars, crossOp, maxMuts


def process_exp(filename: str, sda_states: int, sda_chars: int) -> []:
    fits = []
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            if line.__contains__("fitness"):
                fits.append(int(line.rstrip().split("is")[1].lstrip()))
                pass
            pass
        pass
    return fits


def get_sda(lines: List[str], sda_states: int, sda_chars: int):
    init_state = int(lines[0].rstrip().split("<")[0].rstrip())
    init_char = int(lines[0].rstrip().split("-")[1].strip())
    lines = lines[1:]

    sda_trans = [[] for _ in range(sda_states)]
    sda_resps = [[] for _ in range(sda_states)]
    for state in range(sda_states):
        for char in range(sda_chars):
            one_resp = []
            sda_trans[state].append(int(lines[0].split(">")[1].lstrip().split(" ")[0]))
            line = lines[0].rstrip().split(">")[1].lstrip().split(" ")
            one_resp.append(int(line[2]))
            if len(line) == 5:
                one_resp.append(int(line[3]))
                pass
            sda_resps[state].append(one_resp)
            lines = lines[1:]
            pass
        pass
    return init_state, init_char, sda_trans, sda_resps


def process_sda(filename: str, sda_states: int, sda_chars: int):
    sdas, outputs, fits = [], [], []
    one_sda = []
    with open(filename, "r") as f:
        lines = f.readlines()[1:]
        for line in lines:
            if line.__contains__("SDA"):
                fit_start = True
                pass
            elif fit_start:
                fit_start = False
                sda_start = True
                fits.append(int(line))
                pass
            elif sda_start and not line.__contains__("-"):
                sda_start = False
                line = line.rstrip().split(" ")
                outputs.append(line)
                sdas.append(get_sda(one_sda, sda_states, sda_chars))
                one_sda = []
            elif sda_start:
                one_sda.append(str(line))
                pass
            pass
        pass
    return sdas, outputs, fits


def process_best(filename: str, sda_states: int, sda_chars) -> []:
    sda_lines = []
    sda_flag = False
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            if line.__contains__("Best Run:"):
                run_num = line.rstrip().split(":")[1].split(" ")[1]
                pass
            if line.__contains__("SDA"):
                sda_flag = True
                pass
            elif sda_flag:
                sda_lines.append(line)
                pass
            pass
        pass
    init_state, init_char, sda_trans, sda_resps = get_sda(sda_lines, sda_states, sda_chars)
    return run_num, init_state, init_char, sda_trans, sda_resps


def get_data(filename: str, popsize: int, both: bool):
    vals = []
    if both:
        vals = [[[] for _ in range(popsize)] for _ in range(popsize)]
    else:
        vals = [[] for _ in range(popsize)]
        pass
    fits = []
    with open(filename) as f:
        lines = f.readlines()
        holder = []
        mom = -1
        dad = -1
        for line in lines:
            if line.__contains__("Fitness"):
                started = False
                pass
            elif line.__contains__("Idx"):
                line = line.rstrip()
                if both:
                    line = line.split(": ")[1].split("\t")
                    mom = int(line[0])
                    dad = int(line[1])
                else:
                    line = line.rstrip().split(": ")[1]
                    mom = int(line)
                pass
            elif line.__contains__("Fit"):
                pass
            elif line == "\n":
                if both:
                    vals[mom][dad] = holder
                    vals[dad][mom] = holder
                else:
                    vals[mom] = holder
                    pass
                holder = []
                pass
            elif line.__contains__("Crossover") or line.__contains__("Mutation"):
                started = True
                pass
            elif started:
                line = line.rstrip()
                holder.append(int(line))
                pass
            else:
                line = line.rstrip()
                fits.append(int(line))
                pass
            pass
        pass

    return vals, fits


def make_boxplot(data: [], fits: [], parent_diff: [], first_parent: int, out_path: str, run: int, num_gens: int,
                 popsize: int, metadata: List):
    data = copy.deepcopy(data)
    plt.style.use("seaborn-v0_8")
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)

    f = plt.figure()
    f.set_figheight(4.5)
    f.set_figwidth(10)
    plot = f.add_subplot(111)

    out_path = out_path + "Run" + str(run).zfill(2)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
        pass
    out_path += "/"

    if first_parent > -1:
        out_path = out_path + "P" + str(first_parent + 1).zfill(2)
    else:
        out_path = out_path + "AllP"
        pass

    if not os.path.exists(out_path):
        os.makedirs(out_path)
        pass
    out_path += "/"

    xs = [i + 1 for i in range(popsize)]
    sp = plot.scatter(xs, fits, marker='2', color='#DB57B2', zorder=10, s=100, linewidth=1)

    if first_parent > -1:
        to_del = -1
        for idx in range(popsize):
            if not data[idx]:
                to_del = idx
                pass
            pass
        del data[to_del]
        del xs[to_del]
        pass

    vp = plot.violinplot(data, xs, showmedians=True, widths=0.85)
    for pc in vp["bodies"]:
        pc.set_facecolor("#5770DB")
        pc.set_linewidth(1)
        pc.set_edgecolor("black")
        pass
    for partname in ('cbars', 'cmins', 'cmaxes', 'cmedians'):
        vc = vp[partname]
        vc.set_linewidth(1)
        vc.set_alpha(1)
        vc.set_color("#5770DB")
        pass

    pos_bars, neg_bars, pos_xs, neg_xs = [], [], [], []
    for idx in range(popsize):
        if parent_diff[idx] >= 0:
            pos_xs.append(idx + 1)
            pos_bars.append(parent_diff[idx])
        else:
            neg_xs.append(idx + 1)
            neg_bars.append(parent_diff[idx])
            pass
    posb = plot.bar(pos_xs, pos_bars, color="#57DB80", zorder=0.9)
    negb = plot.bar(neg_xs, neg_bars, color="#DB5F57", zorder=0.9)

    labels = ["Parent's Fitness", "Children's Fitness",
              "Mean of Children's Fitness \u2212 Mean of Parents' Fitness"]
    patches = []
    patches.append(sp)
    patches.append(Patch(color="#5770DB", label="Children's Fitness"))
    patches.append([mpatches.Patch(color="#57DB80", label=labels[2]),
                    mpatches.Patch(color="#DB5F57", label=labels[2])])

    plot.legend(handles=patches, labels=labels, facecolor='white', frameon='true', fontsize=12, framealpha=0.75,
                loc='upper center', ncol=3, borderaxespad=0.1, handler_map={list: HandlerTuple(None)})
    plot.grid(visible="True", axis="y", which='minor', color="white", linewidth=0.5)
    plt.minorticks_on()

    if first_parent > -1:
        f.suptitle("Fitness of Children from 100 " + metadata[0] + " Operations using Parent " +
                   str(first_parent + 1) + " After " + str(num_gens) + " Mating Events", fontsize=14)
        plot.set_xlabel("And Parent", fontsize=12)
    elif first_parent == -2:
        f.suptitle("Fitness of All Children from 100 " + metadata[0] + " Operations After " + str(num_gens) +
                   " Mating Events", fontsize=14)
        plot.set_xlabel("On Parent", fontsize=12)
    else:
        f.suptitle("Fitness of All Children from 100 " + metadata[0] + " Operations After " + str(num_gens) +
                   " Mating Events", fontsize=14)
        plot.set_xlabel("With Parent", fontsize=12)
        pass
    plot.axhline(y=87, color="#0000FF", linestyle="--", linewidth="0.75")

    plt.ylim(-15, 100)
    plt.xlim(0, 51)
    plt.xticks([x for x in range(2, 52, 2)])
    plt.yticks([y for y in range(-10, 100, 10)])
    f.subplots_adjust(bottom=0.1, top=0.93, left=0.03, right=0.99)
    if first_parent > -1:
        f.savefig(out_path + metadata[1] + "_Run" + str(run).zfill(2) + "_P" + str(first_parent + 1).zfill(2) +
                  "_" + str(num_gens).zfill(8) + ".png", dpi=500)
    else:
        f.savefig(out_path + metadata[1] + "_Run" + str(run).zfill(2) + "_AllP_" + str(num_gens).zfill(8) +
                  ".png", dpi=500)
        pass

    plt.close()
    print("Plot for Parent " + str(first_parent + 1) + " after " + str(num_gens) + " generations complete.")
    pass


def edge_list(node_lists, num_nodes):
    edge_lists = []
    for fr in range(num_nodes):
        for to in node_lists[fr]:
            edge_lists.append([fr, to])
            pass
        pass
    return edge_lists


def make_graph(el: [], out_file: str, verts: int):
    g = Digraph(engine="neato")
    e_cout = 0

    g.graph_attr.update(dpi='300', size="6,6", overlap='false')
    # g.node_attr.update(color='black', shape='square', width='0.02', height='0.02')
    g.node_attr.update(color='black', shape='circle', fixedsize='true', width='0.2', fontsize='8')
    g.edge_attr.update(color='black', penwidth='0.25', fixedsize='true', arrowsize='0.2')

    for n in range(verts):
        x = (n % 5)*50
        y = int(n / 5)*50
        if n == 0:
            g.node(str(n), label=str(n), color='red', pos=str(str(x) + "," + str(y) + "!"))
            pass
        else:
            g.node(str(n), label=str(n), pos=str(str(x) + "," + str(y) + "!"))
        pass

    for idx, d in enumerate(el):
        g.edge(str(d[0]), str(d[1]), color='black')
        e_cout += 1
        pass
    g.render(filename=out_file, directory=outp, cleanup=True, format='png', neato_no_op=2)
    del g
    print("Made network: " + out_file + " with " + str(e_cout) + " Edges")
    pass


def main():
    folder_names = os.listdir(inp)
    print_every = 100000

    for fold in folder_names:
        out_path = outp + fold
        if not os.path.exists(out_path):
            os.makedirs(out_path)
            pass
        out_path += "/"

        popsize, sda_states, sda_chars, crossOp, maxMuts= process_readme(inp + fold + "/read.me")
        best_run, init_state, init_char, sda_trans, sda_resps = process_best(inp + fold + "/best.dat",
                                                                             sda_states, sda_chars)
        process_exp(inp + fold + "/exp.dat", sda_states, sda_chars)

        all_crossover_files = os.listdir(inp + fold + "/Crossover Checks/")
        best_run_crossover_files = []
        for file in all_crossover_files:
            if file.__contains__("crossover" + str(best_run).zfill(2)):
                best_run_crossover_files.append(file)
                pass
            pass

        datasets = []
        for file in best_run_crossover_files:
            child_fits_for_parent, parent_fits = get_data(inp + fold + "/Crossover Checks/" + file, popsize, True)
            # child_fits[mom][dad] = list of all children generated from 100 crossovers
            # parent_fits[parent_idx] = fitness value assigned to parent with index parent_idx
            datasets.append([child_fits_for_parent, parent_fits])
            pass

        # ds = [child_fits[], parent_fits[]] at one point of evolution
        for idx, ds in enumerate(datasets):  # for each report
            num_gens = int(best_run_crossover_files[idx].rstrip().split("_")[1].split("k")[0]) * 1000
            all_children_fits_for_parent = []
            # all_parent_means[idx] = the values representing parents mean fitness - children's mean fitness
            all_couple_means = [[] for _ in range(popsize)]

            for mom in range(popsize):
                one_parent_means = []
                for dad in range(popsize):
                    if mom == dad:
                        one_parent_means.append(0)
                    else:
                        parent_mean = (ds[1][mom] + ds[1][dad]) / 2
                        child_mean = np.mean(ds[0][mom][dad])
                        one_parent_means.append(child_mean - parent_mean)
                        pass
                    pass
                all_couple_means[mom] = one_parent_means
                pass

            for parent_idx, child_fits_for_parent in enumerate(ds[0]):
                if num_gens % print_every == 0:
                    make_boxplot(child_fits_for_parent, ds[1], all_couple_means[parent_idx], parent_idx, out_path,
                                 best_run,
                                 num_gens, popsize, [crossOp, "Crossover"])
                    pass
                holder = []
                for vals in child_fits_for_parent:
                    holder.extend(vals)
                    pass
                all_children_fits_for_parent.append(holder)
                pass

            if num_gens % print_every == 0:
                mean_diff = [np.mean(all_children_fits_for_parent[i]) - ds[1][i] for i in range(popsize)]
                make_boxplot(all_children_fits_for_parent, ds[1], mean_diff, -1, out_path, best_run, num_gens, popsize,
                             [crossOp, "Crossover"])
                pass
            pass

        all_mutation_files = os.listdir(inp + fold + "/Mutate Checks/")
        best_run_mutation_files = []
        for file in all_mutation_files:
            if file.__contains__("mutate" + str(best_run).zfill(2)):
                best_run_mutation_files.append(file)
                pass
            pass

        datasets = []
        for file in best_run_mutation_files:
            child_fits_for_parent, parent_fits = get_data(inp + fold + "/Mutate Checks/" + file, popsize, False)
            datasets.append([child_fits_for_parent, parent_fits])
            pass

        for idx, ds in enumerate(datasets):
            num_gens = int(best_run_mutation_files[idx].rstrip().split("_")[1].split("k")[0]) * 1000

            parent_child_diff = []
            for mom in range(popsize):
                parent_fit = ds[1][mom]
                child_mean = np.mean(ds[0][mom])
                parent_child_diff.append(child_mean - parent_fit)
                pass

            if num_gens % print_every == 0:
                make_boxplot(ds[0], ds[1], parent_child_diff, -2, out_path, best_run, num_gens, popsize,
                             ["Sets of Max-" + str(maxMuts) + " Mutation", "Mutation"])
                pass
            pass

        all_sda_checks_files = os.listdir(inp + fold + "/SDA Checks/")
        best_sda_checks_files = []
        for file in all_sda_checks_files:
            if file.__contains__("sda" + str(best_run).zfill(2)):
                best_sda_checks_files.append(file)
                pass
            pass

        # sda_infos = [init_state, init_char, sda_trans, sda_resps]
        for idx, file in enumerate(best_sda_checks_files):
            num_gens = int(best_sda_checks_files[idx].rstrip().split("_")[1].split("k")[0]) * 1000
            sda_infos, sda_outputs, sda_fits = process_sda(inp + fold + "/SDA Checks/" + file, sda_states, sda_chars)
            if num_gens % print_every == 0:
                gc.collect()
                for sda_idx, inf in enumerate(sda_infos):
                    make_graph(edge_list(inf[2], sda_states), fold + "/Run" + str(best_run).zfill(2) + "/SDA_" +
                                str(num_gens).zfill(8) + "_" + str(sda_idx + 1).zfill(2), sda_states)
                    pass
                pass
            pass

    print("DONE")
    pass


main()
