from subprocess import check_output
from pathlib import Path
import re
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

MORE_ICON = 'images/more.png'
RESULT_ICON = 'images/youdao.png'

PRE_SEARCH_ITEM = ExtensionResultItem(icon=MORE_ICON,
                                      name='Type the query',
                                      description='Ready to search...',
                                      on_enter=DoNothingAction())


ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


class PassExtension(Extension):
    """ Extension class, does the searching """

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    """ KeywordQueryEventListener class used to manage user input"""

    def __init__(self):
        self.extension = None

    @staticmethod
    def search(wd_path, keyword):
        """ Do the search """
        working_dir = Path(wd_path).parent.absolute()
        result = check_output([wd_path, keyword],
                              cwd=working_dir).decode()
        return ansi_escape.sub('', result)

    def on_event(self, event, extension):
        """ On user input """

        self.extension = extension

        query_args = event.get_argument()

        if not query_args:
            return RenderResultListAction([PRE_SEARCH_ITEM])

        wd_path = extension.preferences['wdd-path']
        result = self.search(wd_path, query_args)
        item_results = []
        for i in result.split("\n"):
            if len(i.strip()) == 0:
                continue
            item_results.append(ExtensionResultItem(
                icon=RESULT_ICON,
                name=i,
                on_enter=CopyToClipboardAction(query_args)))
        return RenderResultListAction(item_results
                                      )


if __name__ == '__main__':
    PassExtension().run()
