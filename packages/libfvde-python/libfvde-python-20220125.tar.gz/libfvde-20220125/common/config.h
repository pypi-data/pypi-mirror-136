/* common/config.h.  Generated from config.h.in by configure.  */
/* common/config.h.in.  Generated from configure.ac by autoheader.  */

/* Define to 1 if translation of program messages to the user's native
   language is requested. */
#define ENABLE_NLS 1

/* Define to 1 if you have the `AES_cbc_encrypt' function". */
/* #undef HAVE_AES_CBC_ENCRYPT */

/* Define to 1 if you have the `AES_ecb_encrypt' function". */
/* #undef HAVE_AES_ECB_ENCRYPT */

/* Define to 1 if you have the `bindtextdomain' function. */
#define HAVE_BINDTEXTDOMAIN 1

/* Define to 1 if you have the MacOS X function CFLocaleCopyCurrent in the
   CoreFoundation framework. */
/* #undef HAVE_CFLOCALECOPYCURRENT */

/* Define to 1 if you have the MacOS X function CFPreferencesCopyAppValue in
   the CoreFoundation framework. */
/* #undef HAVE_CFPREFERENCESCOPYAPPVALUE */

/* Define to 1 if you have the `chdir' function. */
#define HAVE_CHDIR 1

/* Define to 1 if you have the `clock_gettime' function. */
#define HAVE_CLOCK_GETTIME 1

/* Define to 1 if you have the `close' function. */
#define HAVE_CLOSE 1

/* Define to 1 if you have the <cygwin/fs.h> header file. */
/* #undef HAVE_CYGWIN_FS_H */

/* Define if the GNU dcgettext() function is already present or preinstalled.
   */
#define HAVE_DCGETTEXT 1

/* Define to 1 if debug output should be used. */
/* #undef HAVE_DEBUG_OUTPUT */

/* Define to 1 if you have the declaration of `memrchr', and to 0 if you
   don't. */
#define HAVE_DECL_MEMRCHR 0

/* Define to 1 if you have the declaration of `strerror_r', and to 0 if you
   don't. */
#define HAVE_DECL_STRERROR_R 1

/* Define to 1 if you have the <dlfcn.h> header file. */
#define HAVE_DLFCN_H 1

/* Define to 1 to enable the DllMain function. */
/* #undef HAVE_DLLMAIN */

/* Define to 1 if you have the <errno.h> header file. */
#define HAVE_ERRNO_H 1

/* Define to 1 if you have the `EVP_CIPHER_CTX_cleanup' function". */
/* #undef HAVE_EVP_CIPHER_CTX_CLEANUP */

/* Define to 1 if you have the `EVP_CIPHER_CTX_init' function". */
/* #undef HAVE_EVP_CIPHER_CTX_INIT */

/* Define to 1 if you have the `EVP_aes_128_cbc', `EVP_aes_192_cbc' and
   `EVP_aes_256_cbc' functions". */
#define HAVE_EVP_CRYPTO_AES_CBC 1

/* Define to 1 if you have the `EVP_aes_128_ecb', `EVP_aes_192_ecb' and
   `EVP_aes_256_ecb' functions". */
#define HAVE_EVP_CRYPTO_AES_ECB 1

/* Define to 1 if you have the `EVP_aes_128_xts' and `EVP_aes_256_xts'
   functions". */
/* #undef HAVE_EVP_CRYPTO_AES_XTS */

/* Define to 1 if you have the `EVP_md5' function". */
#define HAVE_EVP_MD5 1

/* Define to 1 if you have the `EVP_MD_CTX_cleanup' function". */
/* #undef HAVE_EVP_MD_CTX_CLEANUP */

/* Define to 1 if you have the `EVP_MD_CTX_init' function". */
/* #undef HAVE_EVP_MD_CTX_INIT */

/* Define to 1 if you have the `EVP_sha1' function". */
#define HAVE_EVP_SHA1 1

/* Define to 1 if you have the `EVP_sha224' function". */
#define HAVE_EVP_SHA224 1

/* Define to 1 if you have the `EVP_sha256' function". */
#define HAVE_EVP_SHA256 1

/* Define to 1 if you have the `EVP_sha512' function". */
#define HAVE_EVP_SHA512 1

/* Define to 1 if you have the `fclose' function. */
#define HAVE_FCLOSE 1

/* Define to 1 if you have the <fcntl.h> header file. */
#define HAVE_FCNTL_H 1

/* Define to 1 if you have the `feof' function. */
#define HAVE_FEOF 1

/* Define to 1 if you have the `fgets' function. */
#define HAVE_FGETS 1

/* Define to 1 if you have the `fgetws' function. */
/* #undef HAVE_FGETWS */

/* Define to 1 if you have the `fmemopen' function. */
#define HAVE_FMEMOPEN 1

/* Define to 1 if you have the `fopen' function. */
#define HAVE_FOPEN 1

/* Define to 1 if you have the `fread' function. */
#define HAVE_FREAD 1

/* Define to 1 if you have the `free' function. */
#define HAVE_FREE 1

/* Define to 1 if you have the `fseeko' function. */
#define HAVE_FSEEKO 1

/* Define to 1 if you have the `fseeko64' function. */
#define HAVE_FSEEKO64 1

/* Define to 1 if you have the `fstat' function. */
#define HAVE_FSTAT 1

/* Define to 1 if you have the `ftruncate' function. */
#define HAVE_FTRUNCATE 1

/* Define to 1 if you have the <fuse.h> header file. */
/* #undef HAVE_FUSE_H */

/* Define to 1 if you have the `fwrite' function. */
#define HAVE_FWRITE 1

/* Define to 1 if you have the `getchar' function. */
#define HAVE_GETCHAR 1

/* Define to 1 if you have the `getcwd' function. */
#define HAVE_GETCWD 1

/* Define to 1 if you have the `getegid' function. */
#define HAVE_GETEGID 1

/* Define to 1 if you have the `getenv' function. */
#define HAVE_GETENV 1

/* Define to 1 if you have the `geteuid' function. */
#define HAVE_GETEUID 1

/* Define to 1 if you have the `getopt' function. */
#define HAVE_GETOPT 1

/* Define if the GNU gettext() function is already present or preinstalled. */
#define HAVE_GETTEXT 1

/* Define to 1 if dlsym function is available in GNU dl. */
#define HAVE_GNU_DL_DLSYM 1

/* Define if you have the iconv() function and it works. */
/* #undef HAVE_ICONV */

/* Define to 1 if you have the <inttypes.h> header file. */
#define HAVE_INTTYPES_H 1

/* Define to 1 if you have the `ioctl' function. */
#define HAVE_IOCTL 1

/* Define if nl_langinfo has CODESET support. */
#define HAVE_LANGINFO_CODESET 1

/* Define to 1 if you have the <langinfo.h> header file. */
#define HAVE_LANGINFO_H 1

/* Define to 1 if you have the `bfio' library (-lbfio). */
/* #undef HAVE_LIBBFIO */

/* Define to 1 if you have the <libbfio.h> header file. */
/* #undef HAVE_LIBBFIO_H */

/* Define to 1 if you have the `caes' library (-lcaes). */
/* #undef HAVE_LIBCAES */

/* Define to 1 if you have the <libcaes.h> header file. */
/* #undef HAVE_LIBCAES_H */

/* Define to 1 if you have the `cdata' library (-lcdata). */
/* #undef HAVE_LIBCDATA */

/* Define to 1 if you have the <libcdata.h> header file. */
/* #undef HAVE_LIBCDATA_H */

/* Define to 1 if you have the `cerror' library (-lcerror). */
/* #undef HAVE_LIBCERROR */

/* Define to 1 if you have the <libcerror.h> header file. */
/* #undef HAVE_LIBCERROR_H */

/* Define to 1 if you have the `cfile' library (-lcfile). */
/* #undef HAVE_LIBCFILE */

/* Define to 1 if you have the <libcfile.h> header file. */
/* #undef HAVE_LIBCFILE_H */

/* Define to 1 if you have the `clocale' library (-lclocale). */
/* #undef HAVE_LIBCLOCALE */

/* Define to 1 if you have the <libclocale.h> header file. */
/* #undef HAVE_LIBCLOCALE_H */

/* Define to 1 if you have the `cnotify' library (-lcnotify). */
/* #undef HAVE_LIBCNOTIFY */

/* Define to 1 if you have the <libcnotify.h> header file. */
/* #undef HAVE_LIBCNOTIFY_H */

/* Define to 1 if you have the `cpath' library (-lcpath). */
/* #undef HAVE_LIBCPATH */

/* Define to 1 if you have the <libcpath.h> header file. */
/* #undef HAVE_LIBCPATH_H */

/* Define to 1 if you have the 'crypto' library (-lcrypto). */
#define HAVE_LIBCRYPTO 1

/* Define to 1 if you have the `csplit' library (-lcsplit). */
/* #undef HAVE_LIBCSPLIT */

/* Define to 1 if you have the <libcsplit.h> header file. */
/* #undef HAVE_LIBCSPLIT_H */

/* Define to 1 if you have the `cthreads' library (-lcthreads). */
/* #undef HAVE_LIBCTHREADS */

/* Define to 1 if you have the <libcthreads.h> header file. */
/* #undef HAVE_LIBCTHREADS_H */

/* Define to 1 if you have the `dl' library (-ldl). */
#define HAVE_LIBDL 1

/* Define to 1 if you have the `fcache' library (-lfcache). */
/* #undef HAVE_LIBFCACHE */

/* Define to 1 if you have the <libfcache.h> header file. */
/* #undef HAVE_LIBFCACHE_H */

/* Define to 1 if you have the `fdata' library (-lfdata). */
/* #undef HAVE_LIBFDATA */

/* Define to 1 if you have the <libfdata.h> header file. */
/* #undef HAVE_LIBFDATA_H */

/* Define to 1 if you have the `fguid' library (-lfguid). */
/* #undef HAVE_LIBFGUID */

/* Define to 1 if you have the <libfguid.h> header file. */
/* #undef HAVE_LIBFGUID_H */

/* Define to 1 if you have the `fplist' library (-lfplist). */
/* #undef HAVE_LIBFPLIST */

/* Define to 1 if you have the <libfplist.h> header file. */
/* #undef HAVE_LIBFPLIST_H */

/* Define to 1 if you have the 'fuse' library (-lfuse). */
#define HAVE_LIBFUSE 1

/* Define to 1 if you have the `fvalue' library (-lfvalue). */
/* #undef HAVE_LIBFVALUE */

/* Define to 1 if you have the <libfvalue.h> header file. */
/* #undef HAVE_LIBFVALUE_H */

/* Define to 1 if you have the `hmac' library (-lhmac). */
/* #undef HAVE_LIBHMAC */

/* Define to 1 if you have the <libhmac.h> header file. */
/* #undef HAVE_LIBHMAC_H */

/* Define to 1 if you have the <libintl.h> header file. */
#define HAVE_LIBINTL_H 1

/* Define to 1 if you have the 'osxfuse' library (-losxfuse). */
/* #undef HAVE_LIBOSXFUSE */

/* Define to 1 if you have the `una' library (-luna). */
/* #undef HAVE_LIBUNA */

/* Define to 1 if you have the <libuna.h> header file. */
/* #undef HAVE_LIBUNA_H */

/* Define to 1 if you have the `z' library (-lz). */
/* #undef HAVE_LIBZ */

/* Define to 1 if you have the <limits.h> header file. */
#define HAVE_LIMITS_H 1

/* Define to 1 if you have the <linux/fs.h> header file. */
#define HAVE_LINUX_FS_H 1

/* Define to 1 if you have the `localeconv' function. */
#define HAVE_LOCALECONV 1

/* Define to 1 if you have the <locale.h> header file. */
#define HAVE_LOCALE_H 1

/* Define to 1 if the local version of libbfio is used. */
#define HAVE_LOCAL_LIBBFIO 1

/* Define to 1 if the local version of libcaes is used. */
#define HAVE_LOCAL_LIBCAES 1

/* Define to 1 if the local version of libcdata is used. */
#define HAVE_LOCAL_LIBCDATA 1

/* Define to 1 if the local version of libcerror is used. */
#define HAVE_LOCAL_LIBCERROR 1

/* Define to 1 if the local version of libcfile is used. */
#define HAVE_LOCAL_LIBCFILE 1

/* Define to 1 if the local version of libclocale is used. */
#define HAVE_LOCAL_LIBCLOCALE 1

/* Define to 1 if the local version of libcnotify is used. */
#define HAVE_LOCAL_LIBCNOTIFY 1

/* Define to 1 if the local version of libcpath is used. */
#define HAVE_LOCAL_LIBCPATH 1

/* Define to 1 if the local version of libcsplit is used. */
#define HAVE_LOCAL_LIBCSPLIT 1

/* Define to 1 if the local version of libcthreads is used. */
#define HAVE_LOCAL_LIBCTHREADS 1

/* Define to 1 if the local version of libfcache is used. */
#define HAVE_LOCAL_LIBFCACHE 1

/* Define to 1 if the local version of libfdata is used. */
#define HAVE_LOCAL_LIBFDATA 1

/* Define to 1 if the local version of libfguid is used. */
#define HAVE_LOCAL_LIBFGUID 1

/* Define to 1 if the local version of libfplist is used. */
#define HAVE_LOCAL_LIBFPLIST 1

/* Define to 1 if the local version of libfvalue is used. */
#define HAVE_LOCAL_LIBFVALUE 1

/* Define to 1 if the local version of libhmac is used. */
#define HAVE_LOCAL_LIBHMAC 1

/* Define to 1 if the local version of libuna is used. */
#define HAVE_LOCAL_LIBUNA 1

/* Define to 1 if you have the `lseek' function. */
#define HAVE_LSEEK 1

/* Define to 1 if you have the `malloc' function. */
#define HAVE_MALLOC 1

/* Define to 1 if you have the `memchr' function. */
#define HAVE_MEMCHR 1

/* Define to 1 if you have the `memcmp' function. */
#define HAVE_MEMCMP 1

/* Define to 1 if you have the `memcpy' function. */
#define HAVE_MEMCPY 1

/* Define to 1 if you have the <memory.h> header file. */
#define HAVE_MEMORY_H 1

/* Define to 1 if you have the `memrchr' function. */
#define HAVE_MEMRCHR 1

/* Define to 1 if you have the `memset' function. */
#define HAVE_MEMSET 1

/* Define to 1 if you have the mkdir function. */
#define HAVE_MKDIR 1

/* Define to 1 if you have the mkdir function with a second mode argument. */
#define HAVE_MKDIR_MODE 1

/* Define to 1 if you have the `mkstemp' function. */
#define HAVE_MKSTEMP 1

/* Define to 1 if multi thread support should be used. */
#define HAVE_MULTI_THREAD_SUPPORT 1

/* Define to 1 if you have the `nl_langinfo' function. */
#define HAVE_NL_LANGINFO 1

/* Define to 1 if you have the `open' function. */
#define HAVE_OPEN 1

/* Define to 1 if you have the <openssl/aes.h> header file. */
/* #undef HAVE_OPENSSL_AES_H */

/* Define to 1 if you have the <openssl/evp.h> header file. */
#define HAVE_OPENSSL_EVP_H 1

/* Define to 1 if you have the <openssl/md5.h> header file. */
/* #undef HAVE_OPENSSL_MD5_H */

/* Define to 1 if you have the <openssl/opensslv.h> header file. */
/* #undef HAVE_OPENSSL_OPENSSLV_H */

/* Define to 1 if you have the <openssl/sha.h> header file. */
/* #undef HAVE_OPENSSL_SHA_H */

/* Define to 1 if you have the <osxfuse/fuse.h> header file. */
/* #undef HAVE_OSXFUSE_FUSE_H */

/* Define to 1 if you have the posix_fadvise function. */
#define HAVE_POSIX_FADVISE 1

/* Define to 1 whether printf supports the conversion specifier "%jd". */
#define HAVE_PRINTF_JD 1

/* Define to 1 whether printf supports the conversion specifier "%zd". */
#define HAVE_PRINTF_ZD 1

/* Define to 1 if you have the 'pthread' library (-lpthread). */
#define HAVE_PTHREAD 1

/* Define to 1 if you have the <pthread.h> header file. */
#define HAVE_PTHREAD_H 1

/* Define to 1 if you have the <Python.h> header file. */
/* #undef HAVE_PYTHON_H */

/* Define to 1 if you have the `read' function. */
#define HAVE_READ 1

/* Define to 1 if you have the `realloc' function. */
#define HAVE_REALLOC 1

/* Define to 1 if you have the `setenv' function. */
#define HAVE_SETENV 1

/* Define to 1 if you have the `setlocale' function. */
#define HAVE_SETLOCALE 1

/* Define to 1 if you have the `setvbuf' function. */
#define HAVE_SETVBUF 1

/* Define to 1 if you have the <signal.h> header file. */
#define HAVE_SIGNAL_H 1

/* Define to 1 if you have the `snprintf' function. */
#define HAVE_SNPRINTF 1

/* Define to 1 if you have the `sscanf' function. */
#define HAVE_SSCANF 1

/* Define to 1 if you have the `stat' function. */
#define HAVE_STAT 1

/* Define to 1 if you have the <stdarg.h> header file. */
#define HAVE_STDARG_H 1

/* Define to 1 if you have the <stdint.h> header file. */
#define HAVE_STDINT_H 1

/* Define to 1 if you have the <stdio.h> header file. */
#define HAVE_STDIO_H 1

/* Define to 1 if you have the <stdlib.h> header file. */
#define HAVE_STDLIB_H 1

/* Define to 1 if you have the `strcasecmp' function. */
#define HAVE_STRCASECMP 1

/* Define to 1 if you have the `strchr' function. */
#define HAVE_STRCHR 1

/* Define to 1 if you have the `strerror' function. */
/* #undef HAVE_STRERROR */

/* Define to 1 if you have the `strerror_r' function. */
#define HAVE_STRERROR_R 1

/* Define to 1 if you have the <strings.h> header file. */
#define HAVE_STRINGS_H 1

/* Define to 1 if you have the <string.h> header file. */
#define HAVE_STRING_H 1

/* Define to 1 if you have the `strlen' function. */
#define HAVE_STRLEN 1

/* Define to 1 if you have the `strncasecmp' function. */
#define HAVE_STRNCASECMP 1

/* Define to 1 if you have the `strncmp' function. */
#define HAVE_STRNCMP 1

/* Define to 1 if you have the `strncpy' function. */
#define HAVE_STRNCPY 1

/* Define to 1 if you have the `strnicmp' function. */
/* #undef HAVE_STRNICMP */

/* Define to 1 if you have the `strrchr' function. */
#define HAVE_STRRCHR 1

/* Define to 1 if you have the `strstr' function. */
#define HAVE_STRSTR 1

/* Define to 1 if you have the `swprintf' function. */
/* #undef HAVE_SWPRINTF */

/* Define to 1 if you have the <sys/disklabel.h> header file. */
/* #undef HAVE_SYS_DISKLABEL_H */

/* Define to 1 if you have the <sys/disk.h> header file. */
/* #undef HAVE_SYS_DISK_H */

/* Define to 1 if you have the <sys/ioctl.h> header file. */
#define HAVE_SYS_IOCTL_H 1

/* Define to 1 if you have the <sys/signal.h> header file. */
#define HAVE_SYS_SIGNAL_H 1

/* Define to 1 if you have the <sys/stat.h> header file. */
#define HAVE_SYS_STAT_H 1

/* Define to 1 if you have the <sys/syslimits.h> header file. */
/* #undef HAVE_SYS_SYSLIMITS_H */

/* Define to 1 if you have the <sys/types.h> header file. */
#define HAVE_SYS_TYPES_H 1

/* Define to 1 if you have the `tcgetattr' function. */
#define HAVE_TCGETATTR 1

/* Define to 1 if you have the `tcsetattr' function. */
#define HAVE_TCSETATTR 1

/* Define to 1 if you have the <termios.h> header file. */
#define HAVE_TERMIOS_H 1

/* Define to 1 if you have the `time' function. */
#define HAVE_TIME 1

/* Define to 1 if you have the `towlower' function. */
/* #undef HAVE_TOWLOWER */

/* Define to 1 if you have the `tzset' function. */
#define HAVE_TZSET 1

/* Define to 1 if you have the <unistd.h> header file. */
#define HAVE_UNISTD_H 1

/* Define to 1 if you have the `unlink' function. */
#define HAVE_UNLINK 1

/* Define to 1 if you have the <varargs.h> header file. */
/* #undef HAVE_VARARGS_H */

/* Define to 1 if verbose output should be used. */
/* #undef HAVE_VERBOSE_OUTPUT */

/* Define to 1 if you have the `vfprintf' function. */
#define HAVE_VFPRINTF 1

/* Define to 1 if you have the `vsnprintf' function. */
#define HAVE_VSNPRINTF 1

/* Define to 1 if you have the <wchar.h> header file. */
#define HAVE_WCHAR_H 1

/* Define to 1 if you have the `wcscasecmp' function. */
/* #undef HAVE_WCSCASECMP */

/* Define to 1 if you have the `wcschr' function. */
/* #undef HAVE_WCSCHR */

/* Define to 1 if you have the `wcslen' function. */
/* #undef HAVE_WCSLEN */

/* Define to 1 if you have the `wcsncasecmp' function. */
/* #undef HAVE_WCSNCASECMP */

/* Define to 1 if you have the `wcsncmp' function. */
/* #undef HAVE_WCSNCMP */

/* Define to 1 if you have the `wcsncpy' function. */
/* #undef HAVE_WCSNCPY */

/* Define to 1 if you have the `wcsnicmp' function. */
/* #undef HAVE_WCSNICMP */

/* Define to 1 if you have the `wcsrchr' function. */
/* #undef HAVE_WCSRCHR */

/* Define to 1 if you have the `wcsstr' function. */
/* #undef HAVE_WCSSTR */

/* Define to 1 if you have the `wcstombs' function. */
/* #undef HAVE_WCSTOMBS */

/* Define to 1 if you have the <wctype.h> header file. */
#define HAVE_WCTYPE_H 1

/* Define to 1 if wide character type should be used. */
/* #undef HAVE_WIDE_CHARACTER_TYPE */

/* Define to 1 if you have the <windows.h> header file. */
/* #undef HAVE_WINDOWS_H */

/* Define to 1 if you have the `wmemchr' function. */
/* #undef HAVE_WMEMCHR */

/* Define to 1 if you have the `wmemcmp' function. */
/* #undef HAVE_WMEMCMP */

/* Define to 1 if you have the `wmemcpy' function. */
/* #undef HAVE_WMEMCPY */

/* Define to 1 if you have the `wmemrchr' function. */
/* #undef HAVE_WMEMRCHR */

/* Define to 1 if you have the `write' function. */
#define HAVE_WRITE 1

/* Define to 1 if you have the 'zlib' library (-lz). */
#define HAVE_ZLIB 1

/* Define to 1 if you have the <zlib.h> header file. */
/* #undef HAVE_ZLIB_H */

/* Define to 1 if you have the `uncompress' function. */
#define HAVE_ZLIB_UNCOMPRESS 1

/* Define to the sub-directory where libtool stores uninstalled libraries. */
#define LT_OBJDIR ".libs/"

/* Name of package */
#define PACKAGE "libfvde"

/* Define to the address where bug reports for this package should be sent. */
#define PACKAGE_BUGREPORT "joachim.metz@gmail.com"

/* Define to the full name of this package. */
#define PACKAGE_NAME "libfvde"

/* Define to the full name and version of this package. */
#define PACKAGE_STRING "libfvde 20220125"

/* Define to the one symbol short name of this package. */
#define PACKAGE_TARNAME "libfvde"

/* Define to the home page for this package. */
#define PACKAGE_URL ""

/* Define to the version of this package. */
#define PACKAGE_VERSION "20220125"

/* The size of `int', as computed by sizeof. */
#define SIZEOF_INT 4

/* The size of `long', as computed by sizeof. */
#define SIZEOF_LONG 8

/* The size of `off_t', as computed by sizeof. */
#define SIZEOF_OFF_T 8

/* The size of `size_t', as computed by sizeof. */
#define SIZEOF_SIZE_T 8

/* The size of `wchar_t', as computed by sizeof. */
#define SIZEOF_WCHAR_T 4

/* Define to 1 if you have the ANSI C header files. */
#define STDC_HEADERS 1

/* Define to 1 if strerror_r returns char *. */
/* #undef STRERROR_R_CHAR_P */

/* Define to 1 if you can safely include both <sys/time.h> and <time.h>. */
#define TIME_WITH_SYS_TIME 1

/* Define to 1 if your <sys/time.h> declares `struct tm'. */
/* #undef TM_IN_SYS_TIME */

/* Version number of package */
#define VERSION "20220125"

/* Define to 1 if `lex' declares `yytext' as a `char *' by default, not a
   `char[]'. */
/* #undef YYTEXT_POINTER */

/* Enable large inode numbers on Mac OS X 10.5.  */
#ifndef _DARWIN_USE_64_BIT_INODE
# define _DARWIN_USE_64_BIT_INODE 1
#endif

/* Number of bits in a file offset, on hosts where this is settable. */
/* #undef _FILE_OFFSET_BITS */

/* Define for large files, on AIX-style hosts. */
/* #undef _LARGE_FILES */

/* Define to empty if `const' does not conform to ANSI C. */
/* #undef const */

/* Define to `int' if <sys/types.h> does not define. */
/* #undef mode_t */

/* Define to `long int' if <sys/types.h> does not define. */
/* #undef off_t */

/* Define to `unsigned int' if <sys/types.h> does not define. */
/* #undef size_t */

/* Define to empty if the keyword `volatile' does not work. Warning: valid
   code using `volatile' can become incorrect without. Disable with care. */
/* #undef volatile */
