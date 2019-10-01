library(TCGAbiolinks)

ctypes = c("BLCA", "BRCA", "CESC", "COAD", "DLBC", "ESCA", "GBM", "HNSC", "KICH", "KIRC", "KIRP", "LAML", 
           "LGG", "LIHC", "LUAD", "LUSC", "OV", "PRAD", "READ", "SARC", "SKCM", "STAD", "THCA", "UCEC", "UVM")
# not in db: COADREAD, GBMLGG, KIPAN, STES
# with 0 WGS records: ACC, CHOL, MESO, PAAD, PCPG, TGCT, THYM, UCS

for (ctype in ctypes) {
    
    query <- GDCquery(project = paste("TCGA", ctype, sep = "-"),
                      data.category = 'Raw sequencing data',
                      experimental.strategy = "WGS",
                      file.type = "bam",
                      legacy = T
    )
    
    data = getResults(query)
    output = paste0("../data/manifests/", ctype, ".query.tsv")
    write.table(data, file = output, sep="\t")

}
