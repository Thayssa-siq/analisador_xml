import os
import json
from django.shortcuts import render
from .forms import XMLUploadForm
from lxml import etree
import google.generativeai as genai
from django.conf import settings

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def extract_xml_content(xml_file):
    try:
        tree = etree.parse(xml_file)
        root = tree.getroot()
        return etree.tostring(root, encoding='unicode')
    except Exception as e:
        return None

def analyze_with_gemini(xml_content):
    if not GEMINI_API_KEY:
        return {'error': 'API KEY não configurada.'}
    prompt = (
        "Sempre Retornar resposta estruturada em JSON, não adicionar textos extras ou comentarios fora do JSON. "
        "Voce será um agente contabilista que vai analisar conteúdos de XMLs e retornar informações sobre CNPJ do emitente, valor total, impostos (ICMS, PIS, COFINS), "
        "data da emissão, resumo com possíveis alertas tributários (por exemplo, valores incoerentes ou impostos ausentes)."
        "\nXML:\n" + xml_content
    )
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Remove bloco markdown se existir
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        try:
            return json.loads(text)
        except Exception as e:
            return {'error': f'Erro ao decodificar JSON: {e}', 'resposta_bruta': response.text}
    except Exception as e:
        return {'error': str(e)}

def upload_xml(request):
    results = []
    error = None
    if request.method == 'POST':
        form = XMLUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('xml_files')
            for f in files:
                xml_content = extract_xml_content(f)
                if not xml_content:
                    results.append({'error': f'Erro ao ler o arquivo {f.name}'})
                    continue
                analysis = analyze_with_gemini(xml_content)
                analysis['filename'] = f.name
                results.append(analysis)
        else:
            error = 'Formulário inválido.'
    else:
        form = XMLUploadForm()
    return render(request, 'uploadxml/upload.html', {'form': form, 'results': results, 'error': error})
