library(HMMcopy)
library(argparser)

p <- arg_parser("correct_gc_and_map")

# Add command line arguments
p <- add_argument(p, "--gc", help = "gc")
p <- add_argument(p, "--map", help = "map")
p <- add_argument(p, "--sample", help = "sample")
p <- add_argument(p, "--out", help = "out")

# Parse the command line arguments
# argv <- parse_args(p, argv = c("--gc", "../data/reference/hg19_gc.wig", 
#                                "--map", "../data/reference/hg19_mapability.wig", 
#                                "--sample", "../data/wigs/LUAD/603e16bf-9b05-49c9-a925-f409626c969a.wig",
#                                "--out", "../data/out"))
argv <- parse_args(p)

uncorrected_reads <- wigsToRangedData(argv$sample, argv$gc, argv$map)
corrected_copy <- correctReadcount(uncorrected_reads)

out <- data.frame(corrected_copy)
write.table(out, argv$out, sep = '\t', col.names=NA)

# plotBias(corrected_copy)
# plotCorrection(corrected_copy)
# plotSegments(corrected_copy, segmented_copy)
