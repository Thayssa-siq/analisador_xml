from django import forms

class XMLUploadForm(forms.Form):
    xml_files = forms.FileField(
        label='Selecione um ou mais arquivos XML de NF-e/CT-e',
        required=True
    )

# TODO: Validar extensões dos arquivos XML

# TODO: Validar extensões dos arquivos XML
