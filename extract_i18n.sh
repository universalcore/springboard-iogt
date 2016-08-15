#!/bin/bash
find . -name '*.mo' -delete
package_name="springboard_iogt"
declare -a unsupported_locales=("tgk_TJ")
mkdir -p ${package_name}/locale

# move out unsupported languages temporarily
for locale in "${unsupported_locales[@]}"
do
	if [ -d "${package_name}/locale/${locale}/" ]; then
		mv "${package_name}/locale/${locale}/" "${package_name}/unsupported_locale/"
	fi
done

python setup.py extract_messages -o ${package_name}/locale/messages.pot

if [ -d "${package_name}/locale/fre_FR/" ]; then
    mv "${package_name}/locale/fre_FR/" "${package_name}/locale/fra_FR/"
fi

for locale in "$@"
do
    if [ ! -f "${package_name}/locale/${locale}/LC_MESSAGES/messages.po" ]; then
        python setup.py init_catalog -i ${package_name}/locale/messages.pot -d ${package_name}/locale -l ${locale}
    fi
done

python setup.py update_catalog -i ${package_name}/locale/messages.pot -d ${package_name}/locale
python setup.py compile_catalog -d ${package_name}/locale


if [ -d "${package_name}/locale/fra_FR/" ]; then
    mv "${package_name}/locale/fra_FR/" "${package_name}/locale/fre_FR/"
fi

# move unsupported languages back and compile
for locale in "${unsupported_locales[@]}"
do
	if [ -d "${package_name}/unsupported_locale/${locale}/" ]; then
		mv "${package_name}/unsupported_locale/${locale}/" "${package_name}/locale/"
		msgfmt -o "${package_name}/locale/${locale}/LC_MESSAGES/messages.mo" "${package_name}/locale/${locale}/LC_MESSAGES/messages.po"
	fi
done


