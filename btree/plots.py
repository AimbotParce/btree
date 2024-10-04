import math
import pathlib
from collections import deque

from PIL import Image, ImageDraw, ImageFont

from .btree_class import BTree, BTreeLeaf, BTreeNode

_font = ImageFont.load_default()

_index_margin = 5
_index_horizontal_padding = 5
_index_vertical_padding = 3
_node_horizontal_margin = 30
_node_vertical_margin = 50


def plotBTree(tree: BTree) -> Image.Image:
    graph_image = _makeSubgraphImage(tree.root)

    tree_image = Image.new(
        mode="RGB",
        size=(graph_image.width + 2 * _node_horizontal_margin, graph_image.height + 2 * _node_vertical_margin),
        color=(255, 255, 255),
    )
    tree_image.paste(graph_image, (_node_horizontal_margin, _node_vertical_margin))
    return tree_image


def _makeSubgraphImage(node: BTreeNode | BTreeLeaf) -> Image.Image:
    """
    Make this node's subgraph image, with this node at the top-most
    """
    node_image = _makeNodeImage(node)
    if isinstance(node, BTreeLeaf):
        return node_image

    children_images = list(map(_makeSubgraphImage, node.children))
    total_width = 0
    total_height = 0
    for img in children_images:
        total_width += img.width
        total_height = max(img.height, total_height)
    total_width += (len(children_images) - 1) * _node_horizontal_margin
    total_height += node_image.height + _node_vertical_margin

    subgraph_image = Image.new(mode="RGB", size=(total_width, total_height), color=(255, 255, 255))
    node_x = subgraph_image.width / 2 - node_image.width / 2
    subgraph_image.paste(node_image, (int(node_x), 0))

    y = _node_vertical_margin + node_image.height
    x = 0
    edge_finish_y = y
    edge_start_y = node_image.height
    for j, img in enumerate(children_images):
        subgraph_image.paste(img, (x, y))
        edge_finish_x = x + img.width / 2
        edge_start_x = node_x + node_image.width / (len(children_images) - 1) * j
        _drawArrow(subgraph_image, (edge_start_x, edge_start_y), (edge_finish_x, edge_finish_y))

        x += img.width + _node_horizontal_margin
    return subgraph_image


def _makeNodeImage(node: BTreeLeaf | BTreeNode) -> Image.Image:
    index_texts = list(map(str, node.indexes)) + [""] * (node.capacity - len(node.indexes))
    max_text_len = max(map(len, index_texts))
    just_texts = map(lambda s: s.ljust(max_text_len), index_texts)

    index_images = list(map(_makeIndexImage, just_texts))
    total_width = 0
    total_height = 0
    for img in index_images:
        total_width += img.width
        total_height = max(img.height, total_height)
    total_height += 2 * _index_margin
    total_width += (len(index_images) + 1) * _index_margin

    node_image = Image.new(mode="RGB", size=(total_width + 2, total_height + 2), color=(255, 255, 255))

    y_center = node_image.height / 2
    x = _index_margin + 1
    for img in index_images:
        y = y_center - img.height / 2
        node_image.paste(img, (x, int(y)))
        x += img.width + _index_margin

    _drawRectangle(node_image, (0, 0), (total_width + 1, total_height + 1), width=1, color=(0, 0, 0))

    return node_image


def _makeIndexImage(index_text: str) -> Image.Image:
    l, t, r, b = _font.getbbox(index_text)
    w = r - l
    h = b - t
    index_image = Image.new(
        mode="RGB",
        size=(2 * _index_horizontal_padding + w + 2, 2 * _index_vertical_padding + h + 2),
        color=(255, 255, 255),
    )
    draw = ImageDraw.Draw(index_image)
    draw.text(
        (1 + _index_horizontal_padding, 1 + _index_vertical_padding),
        index_text,
        font=_font,
        anchor="mm",
        fill=(0, 0, 0),
    )
    _drawRectangle(
        index_image,
        (0, 0),
        (w + 2 * _index_horizontal_padding + 1, h + 2 * _index_vertical_padding + 1),
        width=1,
        color=(0, 0, 0),
    )

    return index_image


def _drawArrow(
    img: Image.Image,
    ptA: tuple[int, int],
    ptB: tuple[int, int],
    width: int = 1,
    color: tuple[int, int, int] = (0, 0, 0),
):
    draw = ImageDraw.Draw(img)
    draw.line((ptA, ptB), width=width, fill=color)

    x0, y0 = ptA
    x1, y1 = ptB
    v = (x1 - x0, y1 - y0)

    norm = math.sqrt(v[0] ** 2 + v[1] ** 2)
    n = (v[0] / norm, v[1] / norm)
    p = (-n[1], n[0])

    # Coordinates of the base of the triangle
    xb = x1 - n[0] * 8
    yb = y1 - n[1] * 8
    vtx0 = (xb + p[0] * 3, yb + p[1] * 3)
    vtx1 = (xb - p[0] * 3, yb - p[1] * 3)
    draw.polygon([vtx0, vtx1, ptB], fill=color)
    return img


def _drawRectangle(
    img: Image.Image,
    ptA: tuple[int, int],
    ptB: tuple[int, int],
    width: int = 1,
    color: tuple[int, int, int] = (0, 0, 0),
):
    draw = ImageDraw.Draw(img)
    minx = min(ptA[0], ptB[0])
    maxx = max(ptA[0], ptB[0])
    miny = min(ptA[1], ptB[1])
    maxy = max(ptA[1], ptB[1])
    draw.line(((minx, miny), (minx, maxy)), fill=color, width=width)
    draw.line(((minx, miny), (maxx, miny)), fill=color, width=width)
    draw.line(((maxx, maxy), (maxx, miny)), fill=color, width=width)
    draw.line(((maxx, maxy), (minx, maxy)), fill=color, width=width)
