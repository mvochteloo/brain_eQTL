"""
File:         dataset.py
Created:      2020/03/16
Last Changed: 2020/03/20
Author:       M.Vochteloo

Copyright (C) 2020 M.Vochteloo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A copy of the GNU General Public License can be found in the LICENSE file in the
root directory of this source tree. If not, see <https://www.gnu.org/licenses/>.
"""

# Standard imports.
import itertools
import os

# Third party imports.

# Local application imports.
from general.df_utilities import load_dataframe


class Dataset:
    def __init__(self, settings):
        self.input_dir = settings.get_setting("input_dir")
        filenames = settings.get_setting("filenames")
        self.eqtl_filename = filenames["eqtl"]
        self.geno_filename = filenames["genotype"]
        self.alleles_filename = filenames["alleles"]
        self.expr_filename = filenames["expression"]
        self.cov_filename = filenames["covariates"]
        self.inter_filename = filenames["interaction"]
        self.markers_filename = filenames["markers"]
        self.celltypes = settings.get_setting("celltypes")
        nrows = settings.get_setting("nrows")
        if not isinstance(nrows, int):
            if isinstance(nrows, str) and (nrows == "" or
                                           nrows.lower() == "all" or
                                           nrows.lower() == "none"):
                nrows = None
            else:
                print("Unexpected argument for nrows")
                exit()
        self.nrows = nrows

        # Declare empty variables.
        self.eqtl_df = None
        self.geno_df = None
        self.alleles_df = None
        self.expr_df = None
        self.cov_df = None
        self.inter_df = None
        self.marker_df = None

    def get_celltypes(self):
        return self.celltypes

    def get_eqtl_df(self):
        if self.eqtl_df is None:
            self.eqtl_df = load_dataframe(inpath=os.path.join(self.input_dir,
                                                              self.eqtl_filename),
                                          header=0,
                                          index_col=False,
                                          nrows=self.nrows)
            self.eqtl_df.index = self.eqtl_df["SNPName"]
            self.eqtl_df.index.name = "-"
            self.validate()
        return self.eqtl_df

    def get_geno_df(self):
        if self.geno_df is None:
            self.geno_df = load_dataframe(inpath=os.path.join(self.input_dir,
                                                              self.geno_filename),
                                          header=0,
                                          index_col=0,
                                          nrows=self.nrows)
            self.validate()
        return self.geno_df

    def get_alleles_df(self):
        if self.alleles_df is None:
            self.alleles_df = load_dataframe(inpath=os.path.join(self.input_dir,
                                                                 self.alleles_filename),
                                             header=0,
                                             index_col=0,
                                             nrows=self.nrows)
            self.validate()
        return self.alleles_df

    def get_expr_df(self):
        if self.expr_df is None:
            self.expr_df = load_dataframe(inpath=os.path.join(self.input_dir,
                                                              self.expr_filename),
                                          header=0,
                                          index_col=0,
                                          nrows=self.nrows)
            self.validate()
        return self.expr_df

    def get_cov_df(self):
        if self.cov_df is None:
            self.cov_df = load_dataframe(inpath=os.path.join(self.input_dir,
                                                             self.cov_filename),
                                         header=0,
                                         index_col=0)
            self.validate()
        return self.cov_df

    def get_inter_df(self):
        if self.inter_df is None:
            self.inter_df = load_dataframe(inpath=os.path.join(self.input_dir,
                                                               self.inter_filename),
                                           header=0,
                                           index_col=0)
            self.validate()
        return self.inter_df

    def get_marker_df(self):
        if self.marker_df is None:
            self.marker_df = load_dataframe(inpath=os.path.join(self.input_dir,
                                                                self.markers_filename),
                                            header=0,
                                            index_col=0)
            self.validate()
        return self.marker_df

    def validate(self):
        dfs = [self.eqtl_df, self.geno_df, self.alleles_df, self.expr_df]
        for (a, b) in list(itertools.combinations(dfs, 2)):
            if a is not None and b is not None and \
                    not a.index.identical(b.index):
                print("Order of eQTLs is not identical (1).")
                exit()

        dfs = [self.geno_df, self.expr_df, self.cov_df]
        for (a, b) in list(itertools.combinations(dfs, 2)):
            if a is not None and b is not None and \
                    not a.columns.identical(b.columns):
                print("Order of samples are not identical.")
                exit()

        if self.cov_df is not None and self.inter_df is not None and \
                not self.cov_df.index.identical(self.inter_df.index):
            print("Order of covariates is not identical.")
            exit()

        if self.inter_df is not None:
            for df in [self.eqtl_df, self.geno_df, self.alleles_df,
                       self.expr_df]:
                if df is not None:
                    subset = self.inter_df.iloc[:, :self.nrows].copy()
                    for i, colname in enumerate(subset.columns):
                        if not colname.startswith(df.index[i]):
                            print("Order of eQTLs is not identical (2).")
                            exit()
                    del subset

        print("\tValid.")
