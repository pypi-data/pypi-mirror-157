import os
import re
import subprocess
import tempfile
from multiprocessing import Pool
from typing import Optional, Collection, Tuple, Dict, List

from tqdm import tqdm

from chiton.fastani.exceptions import FastANIFileNotFound, FastANIException
from chiton.fastani.model import FastANIParameters, FastANIExecution, ExecutionParameters
from chiton.fastani.model import write_genome_list

RE_MISSING_FILE = re.compile(r'ERROR, skch::validateInputFiles, Could not open (.+)')


def execute_mp_wrapper(args: Tuple[FastANIParameters, ExecutionParameters, Dict[str, str]]) -> FastANIExecution:
    """Required as multiprocessing pool will only allow one argument."""
    return execute(params=args[0], exec_params=args[1], **args[2])


def execute(params: FastANIParameters, exec_params: ExecutionParameters, q: Optional[str] = None,
            ql: Optional[Collection[str]] = None,
            r: Optional[str] = None, rl: Optional[Collection[str]] = None) -> FastANIExecution:
    cmd = [params.exe]
    if q is not None:
        cmd.extend(['--query', q])
    if r is not None:
        cmd.extend(['--ref', r])
    cmd.extend(params.k_cmd)
    cmd.extend(params.cpu_cmd)
    cmd.extend(params.frag_len_cmd)
    cmd.extend(params.min_frac_cmd)
    cmd.extend(params.min_frag_cmd)

    with tempfile.TemporaryDirectory(dir=exec_params.tmp_dir) as temp_dir:

        # Set a temporary output file path if output is not set
        out_path = os.path.join(temp_dir, 'output.txt')
        cmd.extend(['--output', out_path])

        # Create a temporary file for the query/ref lists and write to disk
        if ql is not None:
            path_ql = os.path.join(temp_dir, 'query.txt')
            write_genome_list(ql, path_ql)
            cmd.extend(['--queryList', path_ql])
        if rl is not None:
            path_rl = os.path.join(temp_dir, 'reference.txt')
            write_genome_list(rl, path_rl)
            cmd.extend(['--refList', path_rl])

        # Run the proc
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            missing_file = RE_MISSING_FILE.search(stderr)
            if missing_file:
                raise FastANIFileNotFound(missing_file.group(1))
            raise FastANIException(f'Failed to run {params.exe} with error: {stderr}')

        # Package the results and return them
        return FastANIExecution(' '.join(cmd), stdout, stderr, proc.returncode, output=out_path)


def process_queue(
        params: FastANIParameters,
        queue: List[Dict[str, str]],
        exec_params: ExecutionParameters
) -> Tuple[FastANIExecution]:
    # Configure a single temporary directory for files
    with tempfile.TemporaryDirectory(prefix='fastani_', dir=exec_params.tmp_root) as tmp_dir:
        exec_params.set_tmp_dir(tmp_dir)

        # If only using one CPU, don't create a multiprocessing pool
        if params.cpus == 1 or len(queue) <= 1 or params.single_execution:
            if exec_params.show_progress:
                return tuple(execute(params=params, exec_params=exec_params, **cmd) for cmd in tqdm(queue))
            else:
                return tuple(execute(params=params, exec_params=exec_params, **cmd) for cmd in queue)

        # Do single executions, i.e. force FastANI execution to be single threaded
        else:
            mp_cpus = params.cpus
            params.cpus = 1
            mp_queue = [(params, exec_params, cmd) for cmd in queue]
            with Pool(processes=mp_cpus) as pool:
                if exec_params.show_progress:
                    return tuple(tqdm(pool.imap_unordered(execute_mp_wrapper, mp_queue), total=len(mp_queue)))
                else:
                    return tuple(pool.imap_unordered(execute_mp_wrapper, mp_queue))
