#!/usr/bin/env python

# python .\ejemplo1.py subcomando -u doberti

from pycomando import Comando
import logging, sys, pprint

def main():
    comando = Comando(yml='args_ejemplo1.yml')
    arguments_dict = comando.get_arguments_dict()
    logger = comando.get_logger()
    do = arguments_dict.pop("subcommand")

    if do == 'subcomando':
        print('Comando ejecutado exitosamente, se detecto el subcomando:')
        #print(f'Run {comando} with **arguments_dict: {arguments_dict}')
        pprint.pprint(arguments_dict)
    sys.exit(0)

if __name__ == "__main__":
    main()