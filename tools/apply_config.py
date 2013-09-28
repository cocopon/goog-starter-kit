#!/usr/bin/env python


import glob
import os
import re
import toolsconfig


class ApplyConfigCommand(object):
    CONFIG_TARGET_EXT = ('.html', '.xhtml', '.js', '.css')


    def __init__(self, config):
        self.config = config


    @classmethod
    def line_indent(cls, line):
        indent = ''
        m = re.search(r'^(\s*)', line)
        if len(m.groups()) >= 1:
            indent = m.group(1)

        return indent


    @classmethod
    def html_path(cls, path):
        return '/'.join(path.split(os.path.sep))


    def update_base_js(self, line, dirpath):
        path = self.config.base_js()
        relpath = os.path.relpath(path, dirpath)

        return '<script type="text/javascript" src="%s"></script>' % ApplyConfigCommand.html_path(relpath)


    def update_deps_js(self, line, dirpath):
        path = self.config.deps_js()
        relpath = os.path.relpath(path, dirpath)

        return '<script type="text/javascript" src="%s"></script>' % ApplyConfigCommand.html_path(relpath)


    def update_require_main(self, line, dirpath):
        namespace = self.config.main_namespace()
        return '<script type="text/javascript"> goog.require(\'%s\'); </script>' % namespace


    def update_exec_main(self, line, dirpath):
        namespace = self.config.main_namespace()
        return '%s();' % namespace


    def update_provide_main(self, line, dirpath):
        namespace = self.config.main_namespace()
        return 'goog.provide(\'%s\');' % namespace


    def update_main_fn(self, line, dirpath):
        namespace = self.config.main_namespace()
        return '%s = function() {' % namespace


    def update_multitestrunner_css(self, line, dirpath):
        path = self.config.multitestrunner_css()
        relpath = os.path.relpath(path, dirpath)

        return '<link rel="stylesheet" type="text/css" href="%s">' % ApplyConfigCommand.html_path(relpath)


    def apply_config(self, path):
        lines = []
        updaters = {
                '<!--@base_js@-->': update_base_js,
                '<!--@deps_js@-->': self.update_deps_js,
                '/*@exec_main@*/': update_exec_main,
                '/*@main_fn@*/': update_main_fn,
                '/*@provide_main@*/': update_provide_main,
                '<!--@require_main@-->': update_require_main,
                '<!--@multitestrunner_css@-->': update_multitestrunner_css}
        markers = updaters.keys()
        dirpath = os.path.dirname(path)

        for line in open(path):
            for marker in markers:
                if line.find(marker) >= 0:
                    updater = updaters[marker]
                    line = ApplyConfigCommand.line_indent(line) + updater(line, dirpath) + marker + '\n'
            lines.append(line)

        with open(path, 'w') as f:
            for line in lines:
                f.write(line)


    def apply_config_all(self):
        devel_dir = self.config.development_dir()

        # If library_root is in development_dir, we should avoid to walk into the library_root.
        ignores = (
                self.config.library_root(),
                self.config.compiler_root())

        for root, dirs, files in os.walk(devel_dir):
            for filename in files:
                (base, ext) = os.path.splitext(filename)
                if ext not in ApplyConfigCommand.CONFIG_TARGET_EXT:
                    continue

                filepath = os.path.join(root, filename)
                self.apply_config(filepath)

            # Avoid to walk into ignores
            for dirname in dirs:
                if os.path.join(root, dirname) in ignores:
                    dirs.remove(dirname)


    def run(self):
        self.apply_config_all()
