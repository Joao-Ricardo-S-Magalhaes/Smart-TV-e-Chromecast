import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Função para ler e processar os dados
def process_data(file_path):
    df = pd.read_csv(file_path)
    df['bytes_up_log'] = np.log10(df['bytes_up'].replace(0, np.nan))
    df['bytes_down_log'] = np.log10(df['bytes_down'].replace(0, np.nan))
    df['hour'] = pd.to_datetime(df['date_hour']).dt.hour
    return df

# Função para estatísticas gerais
def estatisticas_gerais(df, nome_dispositivo, pdf):
    stats = {
        'Média Upload': df['bytes_up_log'].mean(),
        'Média Download': df['bytes_down_log'].mean(),
        'Desvio Padrão Upload': df['bytes_up_log'].std(),
        'Desvio Padrão Download': df['bytes_down_log'].std(),
        'Variância Upload': df['bytes_up_log'].var(),
        'Variância Download': df['bytes_down_log'].var()
    }

    # Adicionar estatísticas ao PDF
    plt.figure(figsize=(8, 6))
    plt.axis('off')
    plt.title(f'Estatísticas Gerais - {nome_dispositivo}', fontsize=16, weight='bold')
    for i, (key, value) in enumerate(stats.items()):
        plt.text(0, 0.9 - i * 0.1, f'{key}: {value:.2f}', fontsize=12)
    pdf.savefig()
    plt.close()

    return stats

# Função para gerar Box Plots combinados
def box_plots_combinados(smart_tv, chromecast, pdf):
    data = [
        smart_tv['bytes_up_log'].dropna(),
        chromecast['bytes_up_log'].dropna(),
        smart_tv['bytes_down_log'].dropna(),
        chromecast['bytes_down_log'].dropna()
    ]
    labels = ['Upload Smart-TV', 'Upload Chromecast', 'Download Smart-TV', 'Download Chromecast']

    plt.figure(figsize=(10, 6))
    plt.boxplot(data, labels=labels)
    plt.title('Box Plots Comparativos')
    plt.ylabel('Valor Log10')
    pdf.savefig()  # Salvar gráfico no PDF
    plt.close()

# Função para gerar distribuição empírica acumulada
def distribuicao_empirica(dados, nome_dispositivo, titulo, pdf):
    if dados.dropna().empty:
        return  # Evitar gráficos vazios

    dados_ordenados = np.sort(dados.dropna())
    prob_acumulada = np.linspace(0, 1, len(dados_ordenados))

    plt.figure(figsize=(8, 6))
    plt.plot(dados_ordenados, prob_acumulada, marker='.', linestyle='none')
    plt.title(f"{titulo} - {nome_dispositivo}")
    plt.xlabel('Valor Log10')
    plt.ylabel('Probabilidade Acumulada')
    pdf.savefig()  # Salvar gráfico no PDF
    plt.close()

# Função para análise por horário
def analise_por_horario(df, nome_dispositivo, pdf):
    estatisticas_horarias = df.groupby('hour').agg({
        'bytes_up_log': ['mean', 'std'],
        'bytes_down_log': ['mean', 'std']
    })

    if estatisticas_horarias.empty:
        return  # Evitar gráficos vazios

    # Adicionar título de análise por horário ao PDF
    plt.figure(figsize=(8, 6))
    plt.axis('off')
    plt.title(f'Análise por Horário - {nome_dispositivo}', fontsize=16, weight='bold')
    pdf.savefig()
    plt.close()

    # Gerar gráficos
    estatisticas_horarias['bytes_up_log']['mean'].plot(label='Média Upload')
    estatisticas_horarias['bytes_down_log']['mean'].plot(label='Média Download')
    plt.title(f'Média por Hora - {nome_dispositivo}')
    plt.xlabel('Hora')
    plt.ylabel('Valor Log10')
    plt.legend()
    pdf.savefig()
    plt.close()

    return estatisticas_horarias

# Função para histogramas de horários de pico
def histograma_horario_pico(df, nome_dispositivo, hora_pico_upload, hora_pico_download, pdf):
    pico_upload = df[df['hour'] == hora_pico_upload]['bytes_up_log']
    pico_download = df[df['hour'] == hora_pico_download]['bytes_down_log']

    if pico_upload.dropna().empty and pico_download.dropna().empty:
        return  # Evitar gráficos vazios

    # Histograma para upload
    if not pico_upload.dropna().empty:
        plt.hist(pico_upload.dropna(), bins='sturges', alpha=0.7, label='Upload')
        plt.title(f'Histograma - Upload (Hora Pico) - {nome_dispositivo}')
        plt.xlabel('Valor Log10')
        plt.ylabel('Frequência')
        pdf.savefig()
        plt.close()

    # Histograma para download
    if not pico_download.dropna().empty:
        plt.hist(pico_download.dropna(), bins='sturges', alpha=0.7, label='Download')
        plt.title(f'Histograma - Download (Hora Pico) - {nome_dispositivo}')
        plt.xlabel('Valor Log10')
        plt.ylabel('Frequência')
        pdf.savefig()
        plt.close()

# Função para gerar o relatório final
def gerar_relatorio():
    with PdfPages("relatorio_final.pdf") as pdf:
        # Estatísticas gerais
        estatisticas_gerais(smart_tv, 'Smart-TV', pdf)
        estatisticas_gerais(chromecast, 'Chromecast', pdf)

        # Box Plots combinados
        box_plots_combinados(smart_tv, chromecast, pdf)

        # Distribuição empírica acumulada
        distribuicao_empirica(smart_tv['bytes_up_log'], 'Smart-TV', "Distribuição Empírica - Upload", pdf)
        distribuicao_empirica(smart_tv['bytes_down_log'], 'Smart-TV', "Distribuição Empírica - Download", pdf)
        distribuicao_empirica(chromecast['bytes_up_log'], 'Chromecast', "Distribuição Empírica - Upload", pdf)
        distribuicao_empirica(chromecast['bytes_down_log'], 'Chromecast', "Distribuição Empírica - Download", pdf)

        # Análise por horário
        analise_por_horario(smart_tv, 'Smart-TV', pdf)
        analise_por_horario(chromecast, 'Chromecast', pdf)

        # Horários de pico
        hora_pico_smart_tv_upload, hora_pico_smart_tv_download = horarios_maior_trafego(smart_tv)
        hora_pico_chromecast_upload, hora_pico_chromecast_download = horarios_maior_trafego(chromecast)

        # Histogramas dos horários de pico
        histograma_horario_pico(smart_tv, 'Smart-TV', hora_pico_smart_tv_upload, hora_pico_smart_tv_download, pdf)
        histograma_horario_pico(chromecast, 'Chromecast', hora_pico_chromecast_upload, hora_pico_chromecast_download, pdf)

# Função para identificar horários de maior tráfego
def horarios_maior_trafego(df):
    hora_pico_upload = df.groupby('hour')['bytes_up_log'].mean().idxmax()
    hora_pico_download = df.groupby('hour')['bytes_down_log'].mean().idxmax()
    return hora_pico_upload, hora_pico_download

# Carregando e processando os datasets
smart_tv = process_data('dataset_smart-tv.csv')
chromecast = process_data('dataset_chromecast.csv')

# Gerar relatório final
gerar_relatorio()
