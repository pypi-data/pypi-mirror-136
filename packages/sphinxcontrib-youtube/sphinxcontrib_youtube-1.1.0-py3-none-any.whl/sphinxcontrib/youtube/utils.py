#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from docutils import nodes
from docutils.parsers.rst import directives, Directive

CONTROL_HEIGHT = 30


def get_size(d, key):
    if key not in d:
        return None
    m = re.match("(\d+)(|%|px)$", d[key])
    if not m:
        raise ValueError("invalid size %r" % d[key])
    return int(m.group(1)), m.group(2) or "px"


def css(d):
    return "; ".join(sorted("%s: %s" % kv for kv in d.items()))


class video(nodes.General, nodes.Element):
    pass


def visit_video_node(self, node, platform_url):
    aspect = node["aspect"]
    width = node["width"]
    height = node["height"]
    url_parameters = node["url_parameters"]

    if aspect is None:
        aspect = 16, 9

    div_style = {}
    if (height is None) and (width is not None) and (width[1] == "%"):
        div_style = {
            "padding-top": "%dpx" % CONTROL_HEIGHT,
            "padding-bottom": "%f%%" % (width[0] * aspect[1] / aspect[0]),
            "width": "%d%s" % width,
            "position": "relative",
        }
        style = {
            "position": "absolute",
            "top": "0",
            "left": "0",
            "width": "100%",
            "height": "100%",
            "border": "0",
        }
        attrs = {
            "src": "{}{}{}".format(platform_url,node['id'],url_parameters),
            "style": css(style),
        }
    else:
        if width is None:
            if height is None:
                width = 560, "px"
            else:
                width = height[0] * aspect[0] / aspect[1], "px"
        if height is None:
            height = width[0] * aspect[1] / aspect[0], "px"
        style = {
            "width": "%d%s" % width,
            "height": "%d%s" % (height[0] + CONTROL_HEIGHT, height[1]),
            "border": "0",
        }
        attrs = {
            "src":  "{}{}".format(platform_url,node['id']),
            "style": css(style),
        }
    if node["align"] != None: div_style["text-align"] = node["align"]
    attrs["allowfullscreen"] = "true"
    div_attrs = {
        "CLASS": "video_wrapper",
        "style": css(div_style),
    }
    if node["align"] != None: div_attrs["CLASS"] += " align-%s" % node["align"]
    self.body.append(self.starttag(node, "div", **div_attrs))
    self.body.append(self.starttag(node, "iframe", **attrs))
    self.body.append("</iframe></div>")


def depart_video_node(self, node):
    pass


def visit_video_node_latex(self, node, platform, platform_url):
    macro = r"\sphinxcontrib%s" % platform
    if macro not in self.elements["preamble"]:
        self.elements["preamble"] += r"""
        \newcommand{%s}[3]{\begin{quote}\begin{center}\fbox{\url{#1#2#3}}\end{center}\end{quote}}
        """ % macro
    self.body.append('%s{%s}{%s}{%s}\n' % (macro, platform_url, node['id'], node['url_parameters']))


class Video(Directive):
    _node = None # Subclasses should replace with node class.
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "width": directives.unchanged,
        "height": directives.unchanged,
        "aspect": directives.unchanged,
        "align": directives.unchanged,
        "url_parameters": directives.unchanged,
    }

    def run(self):
        if "aspect" in self.options:
            aspect = self.options.get("aspect")
            m = re.match(r"(\d+):(\d+)", aspect)
            if m is None:
                raise ValueError("invalid aspect ratio %r" % aspect)
            aspect = tuple(int(x) for x in m.groups())
        else:
            aspect = None
        if "align" in self.options:
            align = self.options.get("align")
            if align not in ["left", "center", "right"]:
                raise ValueError(
                    "invalid alignment. "
                    "choices are [\"left\", \"center\", \"right\"]"
                )
        else:
            align = None
        width = get_size(self.options, "width")
        height = get_size(self.options, "height")
        url_parameters = self.options.get("url_parameters", "")
        return [self._node(id=self.arguments[0], aspect=aspect, width=width,
                height=height, align=align, url_parameters=url_parameters)]


def unsupported_visit_video(self, node, platform):
    self.builder.warn(
        '{}: unsupported output format (node skipped)'.format(platform)
    )
    raise nodes.SkipNode
