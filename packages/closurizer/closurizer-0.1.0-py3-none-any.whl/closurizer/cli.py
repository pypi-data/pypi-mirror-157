import click
from typing import List
from closurizer.closurizer import add_closure


@click.command()
@click.option('--nodes', help='KGX node file to provide closure labels')
@click.option('--edges', help='KGX edge file to add closure fields to')
@click.option('--closure', default=False, help='TSV file of closure triples')
@click.option('--output', '-o', multiple=True, help='file write kgx file with closure fields added')
@click.option('--field', multiple=True, help='fields to closurize')
def main(nodes: str,
         edges: str,
         closure: str,
         output: str,
         fields: List[str]):
    add_closure(node_file=nodes, edge_file=edges, closure_file=closure, fields=fields, output_file=output)


if __name__ == "__main__":
    main()
