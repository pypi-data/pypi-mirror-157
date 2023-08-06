# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chevy', 'chevy.tests']

package_data = \
{'': ['*']}

install_requires = \
['cachetools>=5.2.0,<6.0.0',
 'msgpack>=1.0.4,<2.0.0',
 'numpy>=1.22.3,<2.0.0',
 'python-chess>=1.999,<2.0',
 'scipy>=1.8.0,<2.0.0']

setup_kwargs = {
    'name': 'chevy',
    'version': '0.2.1',
    'description': 'Chess position Evaluation via hand-crafted features',
    'long_description': '## Simple framework for hand-crafted chess position evaluation\n\n### Installation\n\nTo install please run\n\n```shell\npip install chevy\n```\n\n### Basic usage\n\nKing safety features\n\n```python\nimport chess\nfrom chevy.features import KingSafety\n\n# https://lichess.org/analysis/2r3k1/7R/6PK/6P1/2Q5/8/8/8_b_-_-_6_73\nfen = "2r3k1/7R/6PK/6P1/2Q5/8/8/8 b - - 6 73"\nboard = chess.Board(fen)\n\nking_safety = KingSafety(board, color=chess.WHITE)\nprint(f"{king_safety.king_mobility=}")\nprint(f"{king_safety.castling_rights=}")\nprint(f"{king_safety.king_centrality=}")\nprint(f"{king_safety.checked=}")\nprint(f"{king_safety.king_attackers_looking_at_ring_1=}")\nprint(f"{king_safety.king_defenders_at_ring_1=}")\n# + more\n\n```\n\nPawn structure features\n\n```python\nimport chess\nfrom chevy.features import PawnStructure\n\n# https://lichess.org/editor/5kr1/4pp1p/1Q2q3/1PBP2p1/2P3P1/p7/4P3/1R2K1B1_w_-_-_0_19\nfen = "5kr1/4pp1p/1Q2q3/1PBP2p1/2P3P1/p7/4P3/1R2K1B1 w - - 0 19"\nboard = chess.Board(fen)\npawn_structure = PawnStructure(board, color=chess.WHITE)\nprint(f"{pawn_structure.passed_pawns=}")\nprint(f"{pawn_structure.isolated_pawns=}")\nprint(f"{pawn_structure.blocked_pawns=}")\nprint(f"{pawn_structure.central_pawns=}")\n\n\n```\n\nOther common features\n\n```python\nimport chess\nfrom chevy.features import BoardFeatures\n\n# https://lichess.org/editor/5kr1/4pp1p/1Q2q3/1PBP2p1/2P3P1/p7/4P3/1R2K1B1_w_-_-_0_19\nfen = "5kr1/4pp1p/1Q2q3/1PBP2p1/2P3P1/p7/4P3/1R2K1B1 w - - 0 19"\nboard = chess.Board(fen)\nboard_features = BoardFeatures(board, color=chess.WHITE)\nprint(f"{board_features.bishop_pair=}")\nprint(f"{board_features.fianchetto_queen=}")\nprint(f"{board_features.fianchetto_king=}")\nprint(f"{board_features.queens_mobility=}")\nprint(f"{board_features.open_files_rooks_count=}")\nprint(f"{board_features.connected_rooks=}")\nprint(f"{board_features.connectivity=}")\n# + more \n\n\n\n```\n\nTo run tests:\n\n```shell\npytest chevy/tests \n```\n',
    'author': 'int8',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/int8/chevy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
