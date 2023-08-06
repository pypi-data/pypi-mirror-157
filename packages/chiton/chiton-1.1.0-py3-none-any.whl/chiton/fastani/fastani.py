import tempfile
from typing import Optional, Collection, Union

from chiton.fastani.model import FastANIParameters, FastANIResults, ExecutionParameters
from chiton.fastani.process import process_queue
from chiton.fastani.util import validate_paths
from chiton.fastani.version import get_fastani_version


def fastani(
        query: Union[str, Collection[str]],
        reference: Union[str, Collection[str]],
        k: Optional[int] = None,
        cpus: Optional[int] = None,
        frag_len: Optional[int] = None,
        min_frac: Optional[float] = None,
        min_frag: Optional[int] = None,
        single_execution: bool = True,
        bidirectional: bool = False,
        exe: str = 'fastANI',
        tmp_root: str = tempfile.gettempdir(),
        show_progress: bool = True,
) -> FastANIResults:
    """Run FastANI on a set of paths.

    Args:
        query: Either a path to the query genome, or a collection of paths to query genomes.
        reference: Either a path to the reference genome, or a collection of paths to reference genomes.
        k: kmer size <= 16 (default: 16).
        cpus: Number of CPUs to use (default: 1).
        frag_len: fragment length (default: 3,000).
        min_frac: minimum fraction of genome that must be shared for trusting ANI (default: 0.2) [version >= 1.3].
        min_frag: minimum matched fragments for trusting ANI (default: 50)  [version <= 1.2].
        single_execution: True if --refList and --queryList should be used, otherwise a subprocess will be launched to do 1:1 comparisons.
        bidirectional: True if the ANI should be calculated for query vs reference and vice-versa.
        exe: The path to the execution file.
        tmp_root: The root directory used to write temporary files to.
        show_progress: True if a progress bar should be shown, False otherwise.
    """

    # Transform input to a collection
    query = validate_paths(query)
    reference = validate_paths(reference)

    # Nullify version-specific arguments
    version = get_fastani_version(exe)
    params = FastANIParameters(version=version, exe=exe,
                               k=k, cpus=cpus, frag_len=frag_len,
                               min_frac=min_frac, min_frag=min_frag,
                               single_execution=single_execution,
                               bidirectional=bidirectional)
    exec_params = ExecutionParameters(show_progress=show_progress, tmp_root=tmp_root)

    # Create the queue
    queue = list()

    # Run the single execution (query/reference lists) and return the results
    if params.single_execution:
        queue.append({'ql': query, 'rl': reference})
        if params.bidirectional:
            queue.append({'ql': reference, 'rl': query})

    # Generate a queue of commands
    else:
        for query_path in query:
            for reference_path in reference:
                queue.append({'q': query_path, 'r': reference_path})
                if params.bidirectional:
                    queue.append({'q': reference_path, 'r': query_path})

    # Process the queue and return the result
    executions = process_queue(params, queue, exec_params)
    return FastANIResults(query=query, reference=reference, executions=executions, params=params)
