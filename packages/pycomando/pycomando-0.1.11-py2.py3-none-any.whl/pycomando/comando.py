#!/usr/bin/env python

import getpass
import os, sys, logging
import subprocess

import json
import argparse
# Documentation: https://kislyuk.github.io/argcomplete/
import argcomplete
import pprint
import yaml

import eland as ed
from elasticsearch import Elasticsearch

class CommandException(Exception):
    pass

class Comando:
    def __init__(self, yml='args.yml', elasticsearchlink=None, redis_server=None, redis_port: int = 0, f__version__init__=False):
        self.user = getpass.getuser()
        self.redis_client = None
        self.f__version__init__ = f__version__init__
        if redis_server:
            self.redis_client = self._get_redis_client(redis_server, redis_port)
        
        '''
        self.es = Elasticsearch(
                [elasticsearchlink],
                timeout=60
                )
        '''
        self.yml = yml
        self.parser = self.setup_parser_from_yml(self.yml)
        # Generates the parser based on yaml files
        parser = self.get_parser()
        argcomplete.autocomplete(parser)

    def get_parser(self):
        return self.parser

    # implementar ejemplo para reutilizar este codigo para cualquier generacion de comando
    # https://wikimho.com/es/q/codereview/110108
    def load_yml_settings(self, yml, verbose=False):
        '''
        load script's settings (yaml)
        '''
        settings = ''
        with open(yml) as f:
            try:
                settings = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print("Error in configuration file:")
                logging.error(str(e))
                sys.exit(1)
            except Exception as e:
                # unexpected exception.
                logging.error(str(e), exc_info=e)
                sys.exit(1)
            if verbose:
                print (settings)
        return settings

    def read(self, rel_path: str) -> str:
        here = os.path.abspath(os.path.dirname(__file__))
        # intentionally *not* adding an encoding option to open, See:
        #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
        with open(os.path.join(here, rel_path)) as fp:
            return fp.read()

    def get_version(self, rel_path: str) -> str:
        for line in self.read(rel_path).splitlines():
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        raise RuntimeError("Unable to find version string.")

    def setup_parser_from_yml(self, yml=None, arguments=None, parser=None, verbose=False):

        if not parser:
            arguments = self.load_yml_settings(yml, verbose=False)
            file_name = os.path.basename(sys.argv[0])
            file_name = file_name.split('.')[0]
            desc = 'setup autocomplete with:\n\
            CSH: eval `register-python-argcomplete --shell tcsh {f}`\n\
            BASH: eval "$(register-python-argcomplete {f})"'.format(f=file_name)
            parser = argparse.ArgumentParser(
                arguments['title'],
                description=desc,
                formatter_class=argparse.RawTextHelpFormatter,
            )

            if self.f__version__init__:
                __version__ = self.get_version("__init__.py")

                parser.add_argument(
                "--version", action="version", version=f"{__version__}"
                )

            if verbose: pprint.pprint(arguments)

        for key, val in arguments.items():
            if verbose: print(">>>> {}:{}".format(key,val))
            if key == 'title':
                pass
            else:
                if type(val)!=bool and 'caso' in val:
                    if val['caso']=='arg':
                        try:
                            val.pop('caso')
                            # Details on https://stackoverflow.com/questions/36901/what-does-double-star-asterisk-and-star-asterisk-do-for-parameters
                            parser.add_argument( *key.split(','),**val )
                        except CommandException as e:
                            logging.error(str(e))
                            sys.exit(1)
                        except BrokenPipeError:
                            pass  # Ignore. Something like head is truncating output.
                        except KeyboardInterrupt:
                            sys.exit(1)
                        except Exception as e:
                            # unexpected exception.
                            logging.error(str(e), exc_info=e)
                            sys.exit(1)
                    elif val['caso']=='parser':
                        action_subparsers = parser.add_subparsers(dest=val['dest'])
                        action_subparsers.required = val['required']
                        subparser = action_subparsers.add_parser(
                            key, help=val['help'], description=val['description']
                        )
                        if 'caso' in val:
                            self.setup_parser_from_yml(arguments=val, parser=subparser, verbose=False)
                        else:
                            pass
                    else:
                        message = "Error: The parameter 'caso' is wrong!"
                        print(message)
                        logging.error(message)
                        exit(1)
                else:
                    pass
        return parser

    def load_csv(self, csv_file):
        df = ed.csv_to_eland(csv_file,
                es_client=self.es,
                es_dest_index='<index-name>',
                es_if_exists='replace',
                es_dropna=True,
                es_refresh=True,
                # compression='gzip',
                index_col=0)

    def get_info(self):
        df = self.ed.DataFrame(
        es_client=self.es,
        es_index_pattern="<index-name>"
        )
        print(df.head())
        print(df.info())
        print(df.describe())
        print(df.dtypes)

    def _get_redis_client(self, host, port):
        r = None
        try:
            import redis
            logging.debug(f"Redis {host}:{port}")
            r = redis.Redis(host=host, port=port)
            r.ping()
        except ModuleNotFoundError:
            logging.debug("Redis module not found. (pip install redis)")
            r = None
        except Exception as e:
            logging.warning(f"Redis: {e}")
            r = None
        return r
    
    def runCMD(self, command, stdin_str=None, ignore_return_code=False): 
        stdin_param = None 
        if stdin_str: 
            stdin_param = subprocess.PIPE 
        process = subprocess.Popen( 
            command, 
            shell=True, 
            stdin=stdin_param, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
        ) 
        output, error = process.communicate(stdin_str) 
        logging.debug(f"Command: {command} | Exit status: {process.returncode}") 
        # if process.returncode > 0: 
        #     print("stdout: " + output) 
        #     print("stderr: " + error) 
        if not ignore_return_code and process.returncode > 0: 
            raise Exception( 
                f"ERROR '{command}' (exit code {process.returncode}): {error}" 
            ) 
        else: 
            return output[:-1] #.decode('utf-8')

    def runCMD_cached(self, command, stdin_str=None, ignore_return_code=False):

        if self.redis_client:
            out = self.redis_client.get(f"cmd:{command}")
            if out is not None:
                logging.debug(f"(Cached) Command: {command}")
                return out

        out = self.runCMD(
            command, stdin_str=stdin_str, ignore_return_code=ignore_return_code
        )
        if self.redis_client:
            self.redis_client.set(f"cmd:{command}", out, ex=300)
        return out

    def setup_logging(self, log_level):
        """print logging into stderr"""

        # do not show stack traces on console
        short_formatter = logging.Formatter(
            "%(asctime)s;%(levelname)s;%(message)s", "%Y/%m/%d %H:%M:%S"
        )
        log = logging.getLogger()

        logging_level = logging.ERROR
        if log_level:
            if log_level == "debug":
                logging_level = logging.DEBUG
            elif log_level == "info":
                logging_level = logging.INFO
            elif log_level == "warning":
                logging_level = logging.WARNING
        else:
            env_debug_level = os.getenv("DEBUG_LEVEL", "INFO")
            if env_debug_level == "DEBUG":
                logging_level = logging.DEBUG
            elif env_debug_level == "INFO":
                logging_level = logging.INFO
            elif env_debug_level == "WARNING":
                logging_level = logging.WARNING

        log.setLevel(logging_level)
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(short_formatter)
        # console_handler.setLevel(debug_level) # lower level than root logger set
        log.addHandler(console_handler)

