# swift_build_support/products/tsan_libdispatch.py --------------*- python -*-
#
# This source file is part of the Swift.org open source project
#
# Copyright (c) 2014 - 2019 Apple Inc. and the Swift project authors
# Licensed under Apache License v2.0 with Runtime Library Exception
#
# See https://swift.org/LICENSE.txt for license information
# See https://swift.org/CONTRIBUTORS.txt for the list of Swift project authors
#
# ----------------------------------------------------------------------------

import os

from . import product
from .. import shell


def join_path(p1, p2):
    return os.path.abspath(os.path.join(p1, p2))

class TSanLibDispatch(product.Product):
    @classmethod
    def product_source_name(cls):
        return "tsan-libdispatch-test"

    @classmethod
    def is_build_script_impl_product(cls):
        return False

    def build(self, host_target):
        """Build TSan runtime (compiler-rt)."""
        rt_source_dir = join_path(self.source_dir, '../compiler-rt')
        llvm_build_dir = join_path(self.build_dir, '../llvm-' + host_target)
        libdispatch_path = join_path(self.args.install_destdir, 'usr')

        cmd = [
            'cmake',
            '-GNinja',
            '-B%s' % self.build_dir,
            '-DCMAKE_PREFIX_PATH=%s' % llvm_build_dir,
            '-DCMAKE_C_COMPILER=clang',
            '-DCMAKE_CXX_COMPILER=clang++',
            '-DCMAKE_BUILD_TYPE=Release',
            '-DLLVM_ENABLE_ASSERTIONS=ON',
            '-DCOMPILER_RT_INCLUDE_TESTS=ON',
            '-DCOMPILER_RT_INTERCEPT_LIBDISPATCH=ON',
            '-DCOMPILER_RT_LIBDISPATCH_INSTALL_PATH=%s' % libdispatch_path,
            rt_source_dir]
        shell.call(cmd)

        cmd = ['cmake', '--build', self.build_dir, '--target', 'tsan']
        shell.call(cmd)

    def test(self, host_target):
        """Run check-tsan target with a LIT filter for libdispatch."""
        cmd = ['cmake', '--build', self.build_dir, '--target', 'check-tsan']
        env = {'LIT_FILTER': 'libdispatch'}
        shell.call(cmd, env=env)
