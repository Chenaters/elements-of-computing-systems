#include <stdio.h>
#include <stdint.h>

#define EI_NIDENT 16
#define Elf64_Half uint16_t
#define Elf64_Word uint32_t
#define Elf64_Addr uint64_t
#define Elf64_Off uint64_t
typedef struct {
        unsigned char   e_ident[EI_NIDENT];
        Elf64_Half      e_type;
        Elf64_Half      e_machine;
        Elf64_Word      e_version;
        Elf64_Addr      e_entry;
        Elf64_Off       e_phoff;
        Elf64_Off       e_shoff;
        Elf64_Word      e_flags;
        Elf64_Half      e_ehsize;
        Elf64_Half      e_phentsize;
        Elf64_Half      e_phnum;
        Elf64_Half      e_shentsize;
        Elf64_Half      e_shnum;
        Elf64_Half      e_shstrndx;
} Elf64_Ehdr;

enum{
    ET_NONE = 0,
    ET_REL,
    ET_EXEC,
    ET_DYN,
    ET_CORE,
};

enum{
    EM_NONE = 0,
    EM_M32,
    EM_SPARC,
    EM_386,
    EM_68K,
    EM_88K,
    EM_860 = 7,
    EM_MIPS,
    EM_S370,
    EM_MIPS_RS3_LE,
    EM_PARISC = 15,
    EM_VPP500 = 17,
    EM_SPARC32PLUS,
    EM_960,
    EM_PPC,
    EM_PPC64,
    EM_S390,
    EM_V800 = 36,
    EM_FR20,
    EM_RH32,
    EM_RCE,
    EM_ARM,
    EM_ALPHA,
    EM_SH,
    EM_SPARCV9,
    EM_TRICORE,
    EM_ARC,
    EM_H8_300,
    EM_H8_300H,
    EM_H8S,
    EM_H8_500,
    EM_IA_64,
    EM_MIPS_X,
    EM_COLDFIRE,
    EM_68HC12,
    EM_MMA,
    EM_PCP,
    EM_NCPU,
    EM_NDR1,
    EM_STARCORE,
    EM_ME16,
    EM_ST100,
    EM_TINYJ,
    EM_X86_64,  
    EM_PDSP,
    EM_PDP10,
    EM_PDP11,
    EM_FX66,
    EM_ST9PLUS,
    EM_ST7,
    EM_68HC16,
    EM_68HC11,
    EM_68HC08,
    EM_68HC05,
    EM_SVX,
    EM_ST19,
    EM_VAX,
    EM_CRIS,
    EM_JAVELIN,
    EM_FIREPATH,
    EM_ZSP,
    EM_MMIX,
    EM_HUANY,
    EM_PRISM,
    EM_AVR,
    EM_FR30,
    EM_D10V,
    EM_D30V,
    EM_V850,
    EM_M32R,
    EM_MN10300,
    EM_MN10200,
    EM_PJ,
    EM_OPENRISC,
    EM_ARC_A5,
    EM_XTENSA,
    EM_VIDEOCORE,
    EM_TMM_GPP,
    EM_NS32K,
    EM_TPC,
    EM_SNP1K,
    EM_ST200,
};

static const char *machines[] = {
    [EM_NONE] = "EM_NONE",
    [EM_M32] = "EM_M32",
    [EM_SPARC] = "EM_SPARC",
    [EM_386] = "EM_386",
    [EM_68K] = "EM_68K",
    [EM_88K] = "EM_88K",
    [EM_860] = "EM_860",
    [EM_MIPS] = "EM_MIPS",
    [EM_S370] = "EM_S370",
    [EM_MIPS_RS3_LE] = "EM_MIPS_RS3_LE",
    [EM_PARISC] = "EM_PARISC",
    [EM_VPP500] = "EM_VPP500",
    [EM_SPARC32PLUS] = "EM_SPARC32PLUS",
    [EM_960] = "EM_960",
    [EM_PPC] = "EM_PPC",
    [EM_PPC64] = "EM_PPC64",
    [EM_S390] = "EM_S390",
    [EM_V800] = "EM_V800",
    [EM_FR20] = "EM_FR20",
    [EM_RH32] = "EM_RH32",
    [EM_RCE] = "EM_RCE",
    [EM_ARM] = "EM_ARM",
    [EM_ALPHA] = "EM_ALPHA",
    [EM_SH] = "EM_SH",
    [EM_SPARCV9] = "EM_SPARCV9",
    [EM_TRICORE] = "EM_TRICORE",
    [EM_ARC] = "EM_ARC",
    [EM_H8_300] = "EM_H8_300",
    [EM_H8_300H] = "EM_H8_300H",
    [EM_H8S] = "EM_H8S",
    [EM_H8_500] = "EM_H8_500",
    [EM_IA_64] = "EM_IA_64",
    [EM_MIPS_X] = "EM_MIPS_X",
    [EM_COLDFIRE] = "EM_COLDFIRE",
    [EM_68HC12] = "EM_68HC12",
    [EM_MMA] = "EM_MMA",
    [EM_PCP] = "EM_PCP",
    [EM_NCPU] = "EM_NCPU",
    [EM_NDR1] = "EM_NDR1",
    [EM_STARCORE] = "EM_STARCORE",
    [EM_ME16] = "EM_ME16",
    [EM_ST100] = "EM_ST100",
    [EM_TINYJ] = "EM_TINYJ",
    [EM_X86_64] = "EM_X86_64",
    [EM_PDSP] = "EM_PDSP",
    [EM_PDP10] = "EM_PDP10",
    [EM_PDP11] = "EM_PDP11",
    [EM_FX66] = "EM_FX66",
    [EM_ST9PLUS] = "EM_ST9PLUS",
    [EM_ST7] = "EM_ST7",
    [EM_68HC16] = "EM_68HC16",
    [EM_68HC11] = "EM_68HC11",
    [EM_68HC08] = "EM_68HC08",
    [EM_68HC05] = "EM_68HC05",
    [EM_SVX] = "EM_SVX",
    [EM_ST19] = "EM_ST19",
    [EM_VAX] = "EM_VAX",
    [EM_CRIS] = "EM_CRIS",
    [EM_JAVELIN] = "EM_JAVELIN",
    [EM_FIREPATH] = "EM_FIREPATH",
    [EM_ZSP] = "EM_ZSP",
    [EM_MMIX] = "EM_MMIX",
    [EM_HUANY] = "EM_HUANY",
    [EM_PRISM] = "EM_PRISM",
    [EM_AVR] = "EM_AVR",
    [EM_FR30] = "EM_FR30",
    [EM_D10V] = "EM_D10V",
    [EM_D30V] = "EM_D30V",
    [EM_V850] = "EM_V850",
    [EM_M32R] = "EM_M32R",
    [EM_MN10300] = "EM_MN10300",
    [EM_MN10200] = "EM_MN10200",
    [EM_PJ] = "EM_PJ",
    [EM_OPENRISC] = "EM_OPENRISC",
    [EM_ARC_A5] = "EM_ARC_A5",
    [EM_XTENSA] = "EM_XTENSA",
    [EM_VIDEOCORE] = "EM_VIDEOCORE",
    [EM_TMM_GPP] = "EM_TMM_GPP",
    [EM_NS32K] = "EM_NS32K",
    [EM_TPC] = "EM_TPC",
    [EM_SNP1K] = "EM_SNP1K",
    [EM_ST200] = "EM_ST200",
};

void pr_machine(Elf64_Ehdr *header)
{
    printf("%s\n", machines[header->e_machine]);
}

void pr_type(Elf64_Ehdr *header)
{
    switch (header->e_type) {
        case ET_NONE:
            printf("No file type\n");
            break;
        case ET_REL:
            printf("Relocatable file\n");
            break;
        case ET_EXEC:
            printf("Executable file\n");
            break;
        case ET_DYN:
            printf("Shared object file\n");
            break;
        case ET_CORE:
            printf("Core file\n");
            break;
        default:
            printf("Unknown type\n");
    }
}


int main(){
    Elf64_Ehdr header;
    FILE *fp;

    fp = fopen("wc", "rb");
    fread(&header, sizeof(Elf64_Ehdr), 1, fp);

    printf("%c\n", header.e_ident[1]);

    // Header fields
    pr_type(&header);
    pr_machine(&header);
    printf("Version: %u\n", header.e_version);
    printf("Entry point: 0x%lx\n", header.e_entry);
    printf("Program header offset: %lu\n", header.e_phoff);
    printf("Section header offset: %lu\n", header.e_shoff);
    printf("Flags: 0x%x\n", header.e_flags);
    printf("Header size: %u\n", header.e_ehsize);
    printf("Program header size: %u\n", header.e_phentsize);
    printf("Program header count: %u\n", header.e_phnum);
    printf("Section header size: %u\n", header.e_shentsize);
    printf("Section header count: %u\n", header.e_shnum);
    printf("Section name index: %u\n", header.e_shstrndx);
    return 0;
}