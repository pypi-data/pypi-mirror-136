from typing import Dict
import torch
import torchaudio
import jiwer


class GreedyCTCDecoder(torch.nn.Module):
    def __init__(self, labels, ignore):
        super().__init__()
        self.labels = labels
        self.ignore = ignore

    def forward(self, emission: torch.Tensor) -> str:
        """
        Given a sequence emission over labels, get the best path string
        :param emission: Logit tensors. Shape `[num_seq, num_label]`.
        :return: the resulting transcript
        """
        indices = torch.argmax(emission, dim=-1)  # [num_seq,]
        indices = torch.unique_consecutive(indices, dim=-1)
        indices = [i for i in indices if i not in self.ignore]
        return ''.join([self.labels[i] for i in indices])


def asr(SPEECH_FILE: str):
    """
    Performs ASR on SPEECH_FILE and returns the transcript
    :param SPEECH_FILE: path to the audio file to perform ASR on
    :return: string result of ASR
    """
    torch.random.manual_seed(0)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # print(torch.__version__) # MAKE SURE 1.10.0
    # print(torchaudio.__version__) # MAKE SURE 0.10.0
    # print(device)

    bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
    model = bundle.get_model().to(device)

    waveform, sample_rate = torchaudio.load(SPEECH_FILE)
    waveform = waveform.to(device)

    if sample_rate != bundle.sample_rate:
        waveform = torchaudio.functional.resample(waveform, sample_rate, bundle.sample_rate)

    with torch.inference_mode():
        features, _ = model.extract_features(waveform)

    with torch.inference_mode():
        emission, _ = model(waveform)

    decoder = GreedyCTCDecoder(
        labels=bundle.get_labels(),
        ignore=(0, 1, 2, 3),
    )
    transcript = decoder(emission[0])
    return transcript


def evaluate_audio(SPEECH_FILE: str, TRANSCRIPT: str) -> Dict[str,float]:
    """
    Evaluates the recording quality of an audio by comparing the ASR result to the original transcript
    :param SPEECH_FILE: string file path of the audio file
    :param TRANSCRIPT: original transcript
    :return: dictionary containing 3 fields: word error rate, match error rate, and word information lost
    """
    asr_transcript = asr(SPEECH_FILE)
    asr_transcript = asr_transcript.replace('|', ' ')

    transformation = jiwer.Compose([
        jiwer.Strip(),
        jiwer.ToLowerCase(),
        jiwer.RemoveWhiteSpace(replace_by_space=True),
        jiwer.RemoveMultipleSpaces(),
        jiwer.ReduceToListOfListOfWords(),
    ])

    wer = jiwer.wer(TRANSCRIPT, asr_transcript, truth_transform=transformation, hypothesis_transform=transformation)
    mer = jiwer.mer(TRANSCRIPT, asr_transcript, truth_transform=transformation, hypothesis_transform=transformation)
    wil = jiwer.wil(TRANSCRIPT, asr_transcript, truth_transform=transformation, hypothesis_transform=transformation)

    return {'wer': wer, 'mer': mer, 'wil': wil}