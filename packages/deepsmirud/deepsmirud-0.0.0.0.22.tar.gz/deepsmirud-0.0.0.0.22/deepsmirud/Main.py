__author__ = "Jianfeng Sun"
__version__ = "v1.0"
__copyright__ = "Copyright 2022"
__license__ = "MIT"
__email__ = "jianfeng.sunmt@gmail.com"
__maintainer__ = "Jianfeng Sun"

import urllib.request
import click
from pyfiglet import Figlet
from deepsmirud.Run import predict

vignette1 = Figlet(font='standard')

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(short_help=vignette1.renderText('DeepsmirUD'), context_settings=CONTEXT_SETTINGS)
@click.option('-u', '--url', default='https://github.com/2003100127/deepsmirud/releases/download/model/model.zip', help='URL of deepsmirud models')
@click.option('-o', '--output_path', default='./model.zip', help='output path of deepsmirud models')
def download(url, output_path):
    print(vignette1.renderText('DeepsmirUD'))
    print('downloading...')
    urllib.request.urlretrieve(
        url=url,
        filename=output_path
    )
    print('downloaded!')
    return


class HelpfulCmd(click.Command):
    def format_help(self, ctx, formatter):
        click.echo(vignette1.renderText('DeepsmirUD'))
        click.echo(
            '''
            -m, --method, 
                A deep learning method. It can be any below.
                AlexNet | BiRNN | RNN | Seq2Seq | 
                CNN | ConvMixer64 | DSConv | LSTMCNN |
                MobileNet | ResNet18 | ResNet50 | SEResNet
            '''
        )
        click.echo(
            '''
            -sm, --smile_fpn, a small molecule file that contains only smile strings
            '''
        )
        click.echo(
            '''
            -mir, --fasta_fpn, a miRNA fasta file
            '''
        )
        click.echo(
            '''
            -mf, --model_fp, a model path
            '''
        )
        click.echo(
            '''
            -o, --output_path, outputting deepsmirud predictions
            '''
        )

@click.command(cls=HelpfulCmd, context_settings=CONTEXT_SETTINGS)
@click.option(
    '-m', '--method', default='LSTMCNN',
    help='''
        A deep learning method. It can be any below.
        AlexNet | BiRNN | RNN | Seq2Seq | 
        CNN | ConvMixer64 | DSConv | LSTMCNN |
        MobileNet | ResNet18 | ResNet50 | SEResNet
    '''
)
@click.option('-sm', '--smile_fpn', default='data/example/5757.txt', help='a small molecule file that contains only smile strings')
@click.option('-mir', '--fasta_fpn', default='data/example/MIMAT0000066.fasta', help='a miRNA fasta file')
@click.option('-mf', '--model_fp', default='model/lstmcnn', help='a model path')
@click.option('-o', '--output_path', default='./out.deepsmirud', help='outputting deepsmirud predictions')
def main(
        method,
        smile_fpn,
        fasta_fpn,
        model_fp,
        output_path,
):
    print(vignette1.renderText('DeepsmirUD'))
    print('predicting...')
    deepsmirud_p = predict(
        smile_fpn=smile_fpn,
        fasta_fpn=fasta_fpn,
        method=method,
        model_fp=model_fp,
        sv_fpn=output_path,
    )
    s = [
        'AlexNet',
        'BiRNN',
        'RNN',
        'Seq2Seq',
    ]
    if method in s:
        deepsmirud_p.m1()
    else:
        deepsmirud_p.m2()


if __name__ == '__main__':
    main()