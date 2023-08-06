# Copyright (c) 2022 Mohamed Seleem.
#
# This file is part of sqlfluff-plugin-schema.
# See https://github.com/mselee/sqlfluff-plugin-schema for further info.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


def select_children(
    root,
    start_seg=None,
    stop_seg=None,
    select_if=None,
    loop_while=None,
):
    code_segs = [seg for seg in root.segments if seg.is_code]
    start_index = code_segs.index(start_seg) if start_seg else -1
    stop_index = code_segs.index(stop_seg) if stop_seg else len(code_segs)
    buff = []
    for idx in range(start_index + 1, stop_index):
        seg = code_segs[idx]
        if loop_while and not loop_while(seg):
            break
        if not select_if or select_if(seg):
            buff.append((idx, seg))
    return buff


def select_children_raw(
    root,
    start_seg=None,
    stop_seg=None,
    select_if=None,
    loop_while=None,
):
    childs = select_children(root, start_seg=start_seg, stop_seg=stop_seg, select_if=select_if, loop_while=loop_while)
    return [(idx, seg.raw_upper) for idx, seg in childs]


def sibling_within(childs, margin=1):
    if margin is None:
        return True

    N = len(childs)
    if N < 2:
        return True

    for i in range(0, N - 1):
        left, _ = childs[i]
        right, _ = childs[i + 1]
        if right - left > margin:
            return False

    return True


def select(segment, *types, terms=None, margin=1, raw=True, start=None, stop=None):
    def select_if(segment):
        return segment.is_code and (segment.is_type(*types) if types else True) and (segment in terms if terms else True)

    selector = select_children_raw if raw else select_children
    childs = selector(segment, start_seg=start, stop_seg=stop, select_if=select_if)
    if terms:
        childs = childs[: len(terms)]
    if childs and (not terms or sibling_within(childs, margin=margin)):
        return [child for _, child in childs]
    return []
