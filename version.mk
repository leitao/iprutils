IPR_MAJOR_RELEASE=2
IPR_MINOR_RELEASE=0
IPR_FIX_LEVEL=1
IPR_FIX_DATE=(February 27, 2004)

IPR_VERSION_STR=Ver. $(IPR_MAJOR_RELEASE) Rev. $(IPR_MINOR_RELEASE).$(IPR_FIX_LEVEL)

IPR_DEFINES = -DIPR_MAJOR_RELEASE=$(IPR_MAJOR_RELEASE) \
		 -DIPR_MINOR_RELEASE=$(IPR_MINOR_RELEASE) \
		 -DIPR_FIX_LEVEL=$(IPR_FIX_LEVEL) \
		 -DIPR_FIX_DATE='"$(IPR_FIX_DATE)"' \
		 -DIPR_VERSION_STR='"$(IPR_VERSION_STR)"'
