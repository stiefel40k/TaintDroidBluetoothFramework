from framework.utils import iohelpers


def show_common_uuids(analysis_results, *args):
    """
    Shows common uuid along multiple analysis results
    :param analysis_results: List of AnalysisResults objects
    :type analysis_results: list of AnalysisResults
    :param args: at the first place the can optionally be passed a limit to
        only show the first <limit> UUIDs
    :type args: list
    """
    common_uuids = dict(analysis_results[0].leaked_uuids)
    for analysis_result in analysis_results:
        if len(analysis_result.leaked_uuids.keys()) > len(common_uuids.keys()):
            common_uuids = dict(analysis_result.leaked_uuids)

    for analysis_result in analysis_results:
        to_dump = []
        for common_key in common_uuids.keys():
            if common_key not in analysis_result.leaked_uuids:
                to_dump.append(common_key)
        for uuid in to_dump:
            common_uuids.pop(uuid, None)

    iohelpers.process_show_uuid(common_uuids, args, 'Common-')
    print("From {} separate UUIDs {} were common".format(
        ', '.join([str(len(a.leaked_uuids)) for a in analysis_results]),
        len(common_uuids)))
