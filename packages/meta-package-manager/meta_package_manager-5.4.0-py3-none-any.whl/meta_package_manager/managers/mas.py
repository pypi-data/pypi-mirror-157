# Copyright Kevin Deldycke <kevin@deldycke.com> and contributors.
# All Rights Reserved.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import re

from click_extra.platform import MACOS

from ..base import Package, PackageManager
from ..capabilities import search_capabilities


class MAS(PackageManager):

    name = "Mac AppStore"

    homepage_url = "https://github.com/argon/mas"

    platforms = frozenset({MACOS})

    # 'mas search' output has been fixed in 1.6.1:
    # https://github.com/mas-cli/mas/pull/205
    requirement = "1.6.1"

    version_cli_options = ("version",)
    """
    .. code-block:: shell-session

        ► mas version
        1.8.3
    """

    @property
    def installed(self):
        """Fetch installed packages.

        .. code-block:: shell-session

            ► mas list
            1569813296  1Password for Safari                 (2.3.5)
            1295203466  Microsoft Remote Desktop             (10.7.6)
            409183694   Keynote                              (12.0)
            1408727408  com.adriangranados.wifiexplorerlite  (1.5.5)
            409203825   Numbers                              (12.0)
        """
        output = self.run_cli("list")

        regexp = re.compile(
            r"""
            (?P<package_id>\d+)
            \s+
            (?P<package_name>.+?)
            \s+
            \(
                (?P<version>\S+)
            \)
            """,
            re.MULTILINE | re.VERBOSE,
        )

        for package_id, package_name, version in regexp.findall(output):
            yield Package(id=package_id, name=package_name, installed_version=version)

    @property
    def outdated(self):
        """Fetch outdated packages.

        .. code-block:: shell-session

            ► mas outdated
            409183694  Keynote (11.0 -> 12.0)
            1176895641 Spark   (2.11.20 -> 2.11.21)
        """
        output = self.run_cli("outdated")

        regexp = re.compile(
            r"""
            (?P<package_id>\d+)
            \s+
            (?P<package_name>.+?)
            \s+
            \(
                (?P<installed_version>\S+)
                \s+->\s+
                (?P<latest_version>\S+)
            \)
            """,
            re.MULTILINE | re.VERBOSE,
        )

        for (
            package_id,
            package_name,
            installed_version,
            latest_version,
        ) in regexp.findall(output):
            yield Package(
                id=package_id,
                name=package_name,
                installed_version=installed_version,
                latest_version=latest_version,
            )

    @search_capabilities(extended_support=False, exact_support=False)
    def search(self, query, extended, exact):
        """Fetch matching packages.

        .. caution::
            Search does not support extended or exact matching. So we returns the best subset of results and let
            :py:meth:`meta_package_manager.base.PackageManager.refiltered_search` refine them.

        .. code-block:: shell-session

            ► mas search python
               689176796  Python Runner   (1.3)
               630736088  Learning Python (1.0)
               945397020  Run Python      (1.0)
              1164498373  PythonGames     (1.0)
              1400050251  Pythonic        (1.0.0)
        """
        output = self.run_cli("search", query)

        regexp = re.compile(
            r"""
            (?P<package_id>\d+)
            \s+
            (?P<package_name>.+?)
            \s+
            \(
                (?P<version>\S+)
            \)
            """,
            re.MULTILINE | re.VERBOSE,
        )

        for package_id, package_name, version in regexp.findall(output):
            yield Package(id=package_id, name=package_name, latest_version=version)

    def install(self, package_id):
        """Install one package.

        .. code-block:: shell-session

            ► mas install 945397020
        """
        return self.run_cli("install", package_id)

    def upgrade_cli(self, package_id=None):
        """Generates the CLI to upgrade all packages (default) or only the one provided
        as parameter.

        .. code-block:: shell-session

            ► mas upgrade

        .. code-block:: shell-session

            ► mas upgrade 945397020
        """
        return self.build_cli("upgrade", package_id)
