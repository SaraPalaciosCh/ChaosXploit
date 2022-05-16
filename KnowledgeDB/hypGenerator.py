from argparse import ArgumentParser, ArgumentTypeError
import pygraphviz as pgv


def find_goal(tree):
    gv = pgv.AGraph(tree,
                    strict=False,
                    directed=True)
    goal = gv.get_node('final_goal')
    str_goal = goal.attr['label']
    print(str_goal)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-tree",
                        dest="tree",
                        required=True,
                        help="Tree to be analysed")

    arguments = parser.parse_args()
    find_goal(arguments.tree)
