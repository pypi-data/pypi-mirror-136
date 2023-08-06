import json
import logging
import operator
from pathlib import Path
from typing import Optional

import rich
from github import Github, UnknownObjectException
from ldflex import LDFlex
from octadocs.storage import load_graph
from octadocs_github.models import GH, RepoDescription
from typer import Typer
from urlpath import URL

logger = logging.getLogger(__name__)
app = Typer(
    name='github',
    help='Manage data from GitHub.',
)

SPDX_URL = URL(
    'https://raw.githubusercontent.com/spdx/license-list-data/'
    'master/jsonld/licenses.jsonld',
)


def ldflex_from_cache() -> LDFlex:
    """Instantiate LDFLex from the cached graph."""
    graph = load_graph(Path.cwd() / '.cache/octadocs')
    return LDFlex(graph=graph)


GITHUB_URLS = '''
SELECT DISTINCT ?url WHERE {
    {
        ?url ?p ?o
    } UNION {
        ?s ?p ?url
    }

    FILTER isIRI(?url) .

    FILTER(
        STRSTARTS(
            str(?url),
            "https://github.com/"
        )
    ) .
}
'''


def extract_repo_name(url: URL) -> Optional[str]:
    """Extract repository name from a GitHub URL."""
    try:
        _hostname, owner_name, repo_name, *etc = url.parts
    except ValueError:
        return None

    return f'{owner_name}/{repo_name}'


@app.command(name='update')
def github_cli():
    """Update GitHub information."""
    ldflex = ldflex_from_cache()
    uri_refs = map(
        operator.itemgetter('url'),
        ldflex.query(GITHUB_URLS),
    )

    urls = map(URL, uri_refs)

    repo_names = set(filter(bool, map(extract_repo_name, urls)))

    gh = Github()

    docs_dir = Path.cwd() / 'docs'

    if not docs_dir.is_dir():
        raise ValueError(
            f'{docs_dir} is considered to be docs directory but it does not '
            f'exist.',
        )

    target_dir = docs_dir / 'generated/octadocs-github'
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / 'context.json').write_text(json.dumps(
        {
            '@import': 'github',

            # FIXME: See docs/decisions/0010-context-application-order.md
            '@vocab': str(GH),
        },
        indent=2,
    ))

    for repo_name in repo_names:
        rich.print(f'Downloading: {repo_name}')
        try:
            repo = gh.get_repo(repo_name)
        except UnknownObjectException:
            logger.error(
                '%s is not a valid GitHub repository name.',
                repo_name,
            )
            continue

        formatted_data = repo.raw_data
        formatted_data['@id'] = repo.html_url

        # GitHub does not know the license, so we will not export it.
        spdx_id = formatted_data['license']['spdx_id']
        if spdx_id == 'NOASSERTION':
            formatted_data.pop('license')

        file_name = repo.full_name.replace('/', '__')
        (target_dir / f'{file_name}.json').write_text(json.dumps(
            formatted_data,
            indent=2,
        ))
