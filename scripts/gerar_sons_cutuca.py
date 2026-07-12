#!/usr/bin/env python3
"""Gera a família sonora oficial do Cutuca (WAV 44.1 kHz mono)."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

TAXA = 44100
MOTIVO = (369.99, 440.00, 554.37)  # F#4, A4, C#5


def clamp(valor: float, minimo: float = -1.0, maximo: float = 1.0) -> float:
    return max(minimo, min(maximo, valor))


def envoltoria(indice: int, total: int, ataque: float, liberacao: float) -> float:
    if total <= 0:
        return 0.0
    t = indice / TAXA
    dur = total / TAXA
    if t < ataque:
        return t / ataque if ataque else 1.0
    if t > dur - liberacao:
        resto = max(dur - t, 0.0)
        return resto / liberacao if liberacao else 0.0
    return 1.0


def tom(
    frequencia: float,
    duracao: float,
    volume: float = 0.45,
    ataque: float = 0.018,
    liberacao: float = 0.12,
    brilho: float = 0.18,
) -> list[float]:
    n = int(duracao * TAXA)
    amostras: list[float] = []
    for i in range(n):
        t = i / TAXA
        env = envoltoria(i, n, ataque, liberacao)
        # Sine + harmônicos suaves (orgânico-digital)
        onda = math.sin(2 * math.pi * frequencia * t)
        onda += brilho * math.sin(2 * math.pi * frequencia * 2 * t)
        onda += brilho * 0.35 * math.sin(2 * math.pi * frequencia * 3 * t)
        # Leve triângulo para corpo
        tri = (2 / math.pi) * math.asin(
            max(-1.0, min(1.0, math.sin(2 * math.pi * frequencia * t)))
        )
        mistura = 0.82 * onda + 0.18 * tri
        amostras.append(clamp(mistura * volume * env))
    return amostras


def silencio(duracao: float) -> list[float]:
    return [0.0] * int(duracao * TAXA)


def juntar(*partes: list[float]) -> list[float]:
    resultado: list[float] = []
    for parte in partes:
        resultado.extend(parte)
    return resultado


def normalizar(amostras: list[float], pico: float = 0.9) -> list[float]:
    atual = max((abs(a) for a in amostras), default=0.0)
    if atual <= 0:
        return amostras
    fator = pico / atual
    return [clamp(a * fator) for a in amostras]


def gravar(caminho: Path, amostras: list[float]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(caminho), 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(TAXA)
        frames = b''.join(struct.pack('<h', int(clamp(a) * 32767)) for a in amostras)
        wav.writeframes(frames)


def assinatura_recebido() -> list[float]:
    f1, f2, f3 = MOTIVO
    ciclo = juntar(
        tom(f1, 0.16, volume=0.55, ataque=0.012, liberacao=0.08),
        silencio(0.04),
        tom(f2, 0.16, volume=0.5, ataque=0.012, liberacao=0.08),
        silencio(0.04),
        tom(f3, 0.28, volume=0.48, ataque=0.014, liberacao=0.14, brilho=0.22),
        silencio(0.55),
    )
    return normalizar(ciclo, 0.88)


def assinatura_sainte() -> list[float]:
    f1, f2, _ = MOTIVO
    ciclo = juntar(
        tom(f1, 0.22, volume=0.28, ataque=0.03, liberacao=0.14, brilho=0.12),
        silencio(0.12),
        tom(f2, 0.26, volume=0.26, ataque=0.03, liberacao=0.16, brilho=0.12),
        silencio(0.9),
    )
    return normalizar(ciclo, 0.55)


def assinatura_resposta() -> list[float]:
    _, f2, f3 = MOTIVO
    return normalizar(
        juntar(
            tom(f2, 0.12, volume=0.42, ataque=0.01, liberacao=0.08),
            silencio(0.03),
            tom(f3, 0.22, volume=0.4, ataque=0.012, liberacao=0.14, brilho=0.2),
            silencio(0.05),
        ),
        0.8,
    )


def assinatura_encerrar() -> list[float]:
    f1, f2, _ = MOTIVO
    return normalizar(
        juntar(
            tom(f2, 0.14, volume=0.3, ataque=0.02, liberacao=0.12, brilho=0.1),
            silencio(0.04),
            tom(f1, 0.28, volume=0.26, ataque=0.03, liberacao=0.2, brilho=0.08),
            silencio(0.05),
        ),
        0.7,
    )


def main() -> None:
    raiz = Path(__file__).resolve().parents[1]
    destino = raiz / 'static' / 'sounds'
    arquivos = {
        'cutuca_recebido.wav': assinatura_recebido(),
        'cutuca_sainte.wav': assinatura_sainte(),
        'cutuca_resposta.wav': assinatura_resposta(),
        'cutuca_encerrar.wav': assinatura_encerrar(),
    }
    for nome, amostras in arquivos.items():
        gravar(destino / nome, amostras)

    # Alias compatível com push nativo / canal Android existentes
    gravar(destino / 'buzina.wav', arquivos['cutuca_recebido.wav'])

    android_raw = raiz / 'mobile' / 'android' / 'app' / 'src' / 'main' / 'res' / 'raw'
    if android_raw.exists():
        gravar(android_raw / 'buzina.wav', arquivos['cutuca_recebido.wav'])

    print('Sons gerados em', destino)
    for nome in [*arquivos, 'buzina.wav']:
        print('-', nome)


if __name__ == '__main__':
    main()
