import pyd4
import pandas as pd
import numpy as np


def chrom_bg(sts, ens, chrom_len):
    chrom = np.zeros(chrom_len, dtype=np.int32)
    to_add = np.int32(1)
    for st, en in zip(sts, ens):
        chrom[st:en] += to_add
    print(f"total_coverage = {chrom.sum()}")
    return chrom


df = pd.read_csv("1.bed.gz", sep="\t", header=None, comment="#")
writer = (
    pyd4.D4Builder("1.d4")
    .add_chroms([("chr11", 10_000_000)])
    .for_sparse_data()
    .get_writer()
)
data = chrom_bg(df[1].to_numpy(), df[2].to_numpy(), 10_000_000)
writer.write_np_array("chr11", 0, data)
writer.close()

d4_sum = pyd4.D4File("1.d4")["chr11"].sum()
df_sum = (df[2] - df[1]).sum()

assert d4_sum == df_sum, "{} != {}".format(d4_sum, df_sum)
