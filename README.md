### Salah AlHaismawi

Applied ML engineer. I train models and ship them: document OCR, language models, speech and vision. Most of my recent work is on Arabic, where good open models are still scarce.

[LinkedIn](https://www.linkedin.com/in/salah-alhaismawi-a62696228/) · [Hugging Face](https://huggingface.co/SalahALHaismawi) · [Nuqta OCR](https://salahalhaismawi.github.io/nuqta-ocr/) · [salah322s1@gmail.com](mailto:salah322s1@gmail.com)

---

<a href="https://github.com/SalahAlHaismawi/nuqta-ocr"><img src="https://raw.githubusercontent.com/SalahAlHaismawi/nuqta-ocr/main/assets/nuqta_logo.png" alt="Nuqta OCR" width="220" align="right"></a>

#### Nuqta OCR: open-source Arabic OCR

Two open models (0.8B and 4B) that read Arabic books, scans, tables, IDs and passports, and copy the tashkeel exactly as printed. Released October 2026.

- **#1 on KITAB-Bench and Misraj-DocOCR** among published results (4B)
- The 0.8B model runs fully offline on Android and iPhone
- **~20,000 downloads** on Hugging Face in its first month
- Python library on PyPI: `pip install nuqta-ocr`
- Other developers have built a Windows GUI, an OCRmyPDF plugin and an invoice reader on top of it

[Repository](https://github.com/SalahAlHaismawi/nuqta-ocr) · [Models](https://huggingface.co/SalahALHaismawi/Nuqta-Arabic-OCR-4B) · [Live demo](https://huggingface.co/spaces/SalahALHaismawi/Nuqta-Arabic-OCR) · [Benchmarks compared](https://salahalhaismawi.github.io/nuqta-ocr/best-arabic-ocr/) · [Raw benchmark outputs](https://huggingface.co/datasets/SalahALHaismawi/Arabic-OCR-benchmark-predictions)

<br clear="right">

---

#### Other projects

| Project | What it is |
| --- | --- |
| [**training-doctor**](https://github.com/SalahAlHaismawi/training-doctor) | Watches a training run and flags silent failures (plateaus, exploding gradients, diverging eval loss) with a specific fix for each. |
| [**YOLOv26 fire detection**](https://github.com/SalahAlHaismawi/yolov26-fire-detection) | Real-time fire and smoke detector, 94.9% mAP@50, trained on 8,939 images. ~6,000 downloads on [Hugging Face](https://huggingface.co/SalahALHaismawi/yolov26-fire-detection). |
| [**Talon**](https://github.com/SalahAlHaismawi/Talon-D1-LLM) | A language model written and trained from scratch: RoPE, GQA, SwiGLU, mixture of experts. |
| [**Falcon-H1R UAE laws**](https://huggingface.co/SalahALHaismawi/falcon-h1r-uae-laws) | Falcon-H1R-7B fine-tuned on UAE legislation. |

#### What I work on

- **Document AI:** OCR for Arabic-script languages (Arabic, Jawi), tables, layout and diacritics
- **Model training:** pretraining, supervised fine-tuning and RL, with evaluation against public benchmarks
- **Speech:** ASR fine-tuning and speaker diarization for multilingual, code-switched audio
- **Infrastructure:** distributed training (FSDP), CUDA/Triton kernels, on-prem GPU serving with vLLM and llama.cpp

PyTorch · Transformers · vLLM · llama.cpp · CUDA/Triton · FastAPI · Docker · Kubernetes · TypeScript/React
