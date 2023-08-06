"""
Base class for all collector plugins
"""
import json
import os
from abc import abstractmethod
from typing import Any, List, Optional, final

from hoppr import plugin_utils
from hoppr.base_plugins.hoppr import HopprPlugin, hoppr_process, hoppr_rerunner
from hoppr.result import Result
from hoppr.types.cred_object import CredObject
from hoppr.types.cyclonedx_1_4 import Component
from hoppr.utils import dedup_list


class CollectorPlugin(HopprPlugin):
    """
    Base class for all collector plugins
    """

    @staticmethod
    def _get_repos(comp: Component) -> List[str]:
        """
        Returns all repos listed in all "hoppr:repository:component_search_sequence" properties
        for this component
        """
        repo_list = []

        for prop in comp.properties or []:
            if prop.name == "hoppr:repository:component_search_sequence":
                search_sequence = json.loads(prop.value or "")
                repo_list.extend(search_sequence.get("Repositories", []))

        return dedup_list(repo_list)

    @abstractmethod
    @hoppr_rerunner
    def collect(self, comp: Any, repo_url: str, creds: CredObject = None):
        """
        This method should attempt to collect a single component from the specified URL
        """

    def directory_for(
        self, purl_type: str, repo_url: str, subdir: Optional[str] = None
    ) -> str:
        """
        Identify the directory into which the artifact should be copied
        """

        repo_dir = plugin_utils.dir_name_from_repo_url(repo_url)
        directory = f"{self.context.collect_root_dir}/{purl_type}/{repo_dir}/"
        if subdir is not None:
            directory += f"{subdir}/"
        os.makedirs(directory, exist_ok=True)
        return directory

    @final
    @hoppr_process
    def process_component(self, comp: Component) -> Result:
        """
        Copy a component to the local collection directory structure

        A CollectorPlugin will never return a RETRY result, but handles the retry logic internally.
        """

        logger = self.get_logger()

        result = Result.fail(f"No repository found for purl {comp.purl}")

        # for repo_url in self.context.manifest.get_repos():
        for repo_url in self._get_repos(comp):
            logger.info(  # pylint: disable=logging-fstring-interpolation
                f"Looking in repository: {repo_url}"
            )

            repo_creds = None
            if self.context.credentials is not None:
                repo_creds = self.context.credentials.find_credentials(repo_url)

            result = self.collect(comp, repo_url, repo_creds)

            if result.is_success():
                break  ### We found it, no need to try any more repositories

        return result
