#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2018 Sunaina Pai
# With modifications since June 2018 copyright (c) Ben
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""Static website/blog generator."""


from collections import defaultdict
from datetime import datetime
import glob
import os
import re
import shutil


def fread(filename):
    """Read file and close the file."""
    with open(filename, 'r') as f:
        return f.read()


def fwrite(filename, text):
    """Write content to file and close the file."""
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)

    with open(filename, 'w') as f:
        f.write(text)


def read_content(path):
    """Read content and metadata from file into a dictionary."""
    text = fread(path)
    name = os.path.basename(path).split('.')[0]
    category = os.path.dirname(path).split('/')[-1]
    date = datetime.fromtimestamp(os.path.getmtime(path))

    return {
        'category': category,
        'content': text,
        'date': date.strftime('%Y-%m-%d'),
        'full_date': date.strftime('%Y-%m-%d %H:%M:%S'),
        'slug': name,
        'title': name.replace('-', ' ').title(),
    }


def render(template, **params):
    """Replace placeholders in template with values from params."""
    return re.sub(
        r'{{\s*([^}\s]+)\s*}}',
        lambda match: str(params.get(match.group(1), match.group(0))),
        template,
    )


def make_pages(src, dst, layout, **params):
    """Generate pages from page content."""
    items = []

    for src_path in glob.glob(src):
        content = read_content(src_path)
        items.append(content)

        params.update(content)

        dst_path = render(dst, **params)
        output = render(layout, **params)

        fwrite(dst_path, output)

    return sorted(items, key=lambda x: x['date'], reverse=True)


def make_list(posts, dst, list_layout, item_layout, **params):
    """Generate list page for a blog."""
    items = []
    for post in posts:
        item_params = dict(params, **post)
        item = render(item_layout, **item_params)
        items.append(item)

    params['content'] = ''.join(items)
    dst_path = render(dst, **params)
    output = render(list_layout, **params)

    fwrite(dst_path, output)


def by_category(posts):
    posts_by_category = defaultdict(list)
    for post in posts:
        posts_by_category[post['category']].append(post)

    return posts_by_category


def main():
    # Create a new _site directory from scratch.
    if os.path.isdir('_site'):
        shutil.rmtree('_site')
    shutil.copytree('static', '_site')

    # Default parameters.
    params = {
        'base_path': '',
        'title': 'Shobute',
        'site_url': 'http://localhost:8000',
        'current_year': datetime.now().year
    }

    # Load layouts.
    page_layout = fread('layout/page.html')
    post_layout = fread('layout/post.html')
    list_layout = fread('layout/list.html')
    item_layout = fread('layout/item.html')
    feed_xml = fread('layout/feed.xml')
    item_xml = fread('layout/item.xml')

    # Combine layouts to form final layouts.
    post_layout = render(page_layout, content=post_layout)
    list_layout = render(page_layout, content=list_layout)

    # Create site pages.
    make_pages(
        'content/[!_]*.html',
        '_site/{{ slug }}/index.html',
        page_layout,
        **params,
    )

    # Create blogs.
    blog_posts = make_pages(
        'content/*/*.html',
        '_site/{{ category }}/{{ slug }}/index.html',
        post_layout,
        **params,
    )

    # Create blog list pages.
    make_list(blog_posts, '_site/index.html', list_layout, item_layout, **params)
    for category, posts in by_category(blog_posts).items():
        make_list(
            posts,
            '_site/{{ category }}/index.html',
            list_layout,
            item_layout,
            category=category,
            **params,
        )

    # Create RSS feeds.
    make_list(blog_posts, '_site/rss.xml', feed_xml, item_xml, **params)


if __name__ == '__main__':
    main()
