"""RedBrick Slicer Integration Package."""
__version__ = "0.0.1b4"


def get_task(
    url: str, user_id: str, token: str, endpoint: str = "https://api.redbrickai.com"
) -> None:
    """Interact with a RedBrick task in 3D Slicer application.

    ### Usage:
    ----------------
    __import__('redbrick_slicer').get_task(url, user_id, token, [endpoint])
    """
    # pylint: disable=import-outside-toplevel
    from redbrick_slicer.common.context import RBContext
    from redbrick_slicer.repo import ProjectRepo, LabelingRepo, ExportRepo
    from redbrick_slicer.slicer import RBSlicer

    context = RBContext(endpoint, token)
    context.export = ExportRepo(context.client)
    context.labeling = LabelingRepo(context.client)
    context.project = ProjectRepo(context.client)
    RBSlicer(context, url, user_id).get_task()
