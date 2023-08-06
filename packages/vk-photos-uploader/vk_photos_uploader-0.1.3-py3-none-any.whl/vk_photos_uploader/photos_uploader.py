from os import environ
from os.path import join, isfile

import click
import vk_api
from tqdm import tqdm

LINE_BREAK = '\n===========================================================\n'
PASSWORD = 'password'


def get_larger_photo_url(photos):
    """
    This function retrieves larger photo id and url.
    :param photos: photos uploading response dictionary
    :return: dictionary consisting of larger photo id and url
    """
    upload_info = dict()
    for photo in photos:
        sizes = photo['sizes']
        width, url = 0, ''
        for size in sizes:
            if size['width'] > width:
                width = size['width']
                url = size['url']
        upload_info[photo['id']] = url
    return upload_info


def display_urls_info_table(dict_data: dict):
    photo_id, url = 'Photo id', 'Url'
    print(f'{photo_id:15}{url}')
    print('--------------------')
    for key, value in dict_data.items():
        print(f'{key:<15}{value}')
        print('--------------------')


def debug_traceback():
    from traceback import format_exc
    print(format_exc())


class ConvertStrToList(click.Option):
    """ This is a converter for 'string-to-list' option. """
    def type_cast_value(self, ctx, value):
        try:
            if isinstance(value, list):
                return value
            value = str(value)
            list_of_items = [v.strip() for v in value.split(',')]
            return list_of_items
        except Exception:
            raise click.BadParameter(value)


class PythonLiteralOption(click.Option):
    """
    This class does the same as 'ConvertStrToList' with 'ast' module.
    """
    def type_cast_value(self, ctx, value):
        import ast
        try:
            return ast.literal_eval(value)
        except Exception as exc:
            raise click.BadParameter(value)


def display_args_opts(args_options: dict):
    """ This function displays user input. """
    print(f'{LINE_BREAK}')
    print('> Your info\n')
    for key, value in args_options.items():
        if key != PASSWORD:
            print(f'{key:20}{value}')
        else:
            print(f'{key:20}{"*" * len(value)}')


def check_photos_existence(source_folder, photos):
    uploading_photos, invalid_paths = [], []
    for photo in photos:
        if isfile(photo_path := join(source_folder, photo)):
            uploading_photos.append(photo_path)
            continue
        invalid_paths.append(photo)
    return uploading_photos, invalid_paths


def print_invalid_paths(folder, photos):
    if photos:
        print(f'{LINE_BREAK}')
        print('> WARNING')
        print('There are no such photos in provided folder:')
        print(f'{folder = }')
        iter_photos = '  \n - '.join(photos)
        print(f' - {iter_photos}')


def upload_photos__bulk(vk_upload, uploading_photos, album_id,
                        caption, description):
    """
    This function uploads given photos with a single API request.
    The given caption and description will be the same for all photos.
    """
    uploaded_photo = vk_upload.photo(
        photos=uploading_photos,
        album_id=album_id,
        caption=caption,
        description=description)
    return get_larger_photo_url(uploaded_photo)


def upload_photos__singly(vk_upload, uploading_photos, album_id):
    """
    This function uploads given photos one by one.
    Each photo name will be used as a caption and as a description.
    """
    larger_photo_urls = {}
    for photo in tqdm(uploading_photos, desc='Uploading ... ',
                      leave=True, unit="photo", colour='green'):
        photo_name = photo.split('/')[-1]
        pure_photo_name = photo_name[:photo_name.rfind('.')]
        uploaded_photo = vk_upload.photo(
            photos=[photo],
            album_id=album_id,
            caption=pure_photo_name,
            description=pure_photo_name)
        larger_photo_url = get_larger_photo_url(uploaded_photo)
        larger_photo_urls.update(larger_photo_url)
    return larger_photo_urls


def vk_auth(username, password):
    """
    This function logs user in and returns object that allows to work with
    vk APIs
    :param username: username, email, phone
    :param password: user password
    :return: vk_api.upload.VkUpload instance
    """
    try:
        vk_session = vk_api.VkApi(username, password)
        vk_session.auth()
    except vk_api.exceptions.BadPassword as exc:
        raise Exception(
            f'\n\n> {exc}\nCheck your password or username/email/phone.')
    except Exception as exc:
        raise Exception(f'\n\n> {exc}')
    vk_session.get_api()
    return vk_api.upload.VkUpload(vk_session)


def vk_upload(upload, uploading_photos, album_id, caption, description):
    """
    This function uses given 'upload' object to upload photos to the vk album
    :param upload: vk_api.upload.VkUpload instance
    :param uploading_photos: list of photos
    :param album_id: vk album id
    :param caption: caption for all photos or an empty string
    :param description: description for all photos or an empty string
    """

    larger_photo_urls = {}
    if caption:  # bulk uploading
        try:
            larger_photo_urls = upload_photos__bulk(
                upload, uploading_photos, album_id, caption, description)
        except Exception as exc:
            print(f'\n> EXCEPTION: \n{exc}')
            debug_traceback()
    else:  # one-by-one uploading
        try:
            larger_photo_urls = upload_photos__singly(
                upload, uploading_photos, album_id)
        except Exception as exc:
            print(f'\n> EXCEPTION: \n{exc}')
            debug_traceback()
    print(f'{LINE_BREAK}\nUploaded photo(s) info:')
    display_urls_info_table(larger_photo_urls)


def upload_photos(username, password,
                  uploading_photos, album_id,
                  caption, description):
    """
    This function signs in the user and uploads photos to the album
    :param username: vk account's username which is email or phone
    :param password: vk account's password
    :param uploading_photos: list of photos
    :param album_id: VK album id
    :param caption: caption for all photos or an empty string
    :param description: description for all photos or an empty string
    :return:
    """
    if not uploading_photos:
        print(f'{LINE_BREAK}\n> WARNING:: there is no photos to upload.')
        return
    try:
        upload = vk_auth(username, password)
        vk_upload(upload, uploading_photos, album_id, caption, description)
    except Exception as exc:
        print(exc)
        return


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--username', '--user', '--email', '--phone',
              required=True,
              prompt=True,
              show_default=True,
              default=lambda: environ.get('USER', ''),
              help='VK account\'s username which is email or phone.')
@click.password_option(f'--{PASSWORD}', '--pass',
                       required=True,
                       confirmation_prompt=False,
                       help='VK account\'s password.')
@click.option("--source_folder", '--folder',
              required=False,
              type=str,
              # cls=ConvertStrToList,
              multiple=False,
              prompt='Folder that contains photos(optional)',
              # prompt_required=True,
              default='',
              show_default=False,
              help='Your local folder, that contains photo(s).'
                   ' You can skip this and provide full path of each photo.')
@click.option("--photos", '-p',
              required=True,
              cls=ConvertStrToList,
              multiple=True,
              prompt='Comma separated photo name(s) or path(s)',
              # prompt_required=True,
              help='Single or multiple photo names from the provided folder.'
                   ' If \'source_folder\' option is not provided,'
                   ' you should pass full path of each photo.'
                   ' If you run script with no arguments, than at prompting'
                   ' you can pass multiple photo names separated by commas,'
                   ' or use "-p" multiple time with all other arguments'
                   ' if you want to upload your photos at once.')
@click.option('--vk_album_id', '--album_id', '--album', '--dest',
              required=True,
              type=int,
              prompt=True,
              help='VK album id, where the photos should be uploaded.')
@click.option('--caption', '--cap',
              required=False,
              type=(str or int),
              prompt='Caption for photo(s)',
              default='',
              help='A caption for photo(s), note, if it is provided, than the'
                   ' same caption will be used for all photos, otherwise each'
                   ' photo\'s name will be used as its caption.')
@click.option('--description', '--desc',
              required=False,
              type=(str or int),
              prompt='Description for photo(s)',
              default='',
              help='A description for photo(s), note, if it is provided, than'
                   ' the same description will be used for all photos,'
                   ' otherwise each photo\'s name will be used as its'
                   ' description.')
def upload_photos_to_album(username, password,
                           source_folder,
                           photos,
                           vk_album_id,
                           caption, description):
    """
    Simple program that uploads given photos to vk photo album.
    Each option has its alternative and/or short name that brings its
    facilities while working.

    \b
    Examples:


    \b
    1. Pass all arguments at the same time:
        $ python photos_uploader.py
            --email gevorg_vardanyan@protonmail.ch
            --pass '<PASSWORD>'
            --source_folder '/home/gevorg/Pictures'
            -p 1.png
            -p 2.png
            -p 3.png
            --vk_album_id 111222333
            --caption 'This is a caption for all photos'
            --desc 'This is a description for all photos'

    - NOTE: Wrap folder name, photo name, caption and description with quotes
    if they contain whitespace(s).


    \b
    \b
    2. Or run script and give each argument separately:
        $ python photos_uploader.py

    - In this case, when you are prompted, you can pass multiple photos
    like this:  1.png, 2.png, 3.jpg

    \b
    \b
    3. Pass photos from different folders:
        $ python photos_uploader.py
            --email gevorg_vardanyan@protonmail.ch
            --pass '<PASSWORD>'
            -p '/home/gevorg/Pictures/1.png'
            -p '/home/gevorg/Photos/2.png'
            -p '/home/gevorg/Images/3.png'
            --vk_album_id 111222333
            --cap 'This is a caption for all photos'
            --desc 'This is a description for all photos'

    - NOTE: Hit 'ENTER' when you are prompted to provide source folder name
    and leave it blank.

    \b
    \b
    4. Skip caption and description:
        $ python photos_uploader.py
            --email gevorg_vardanyan@protonmail.ch
            --pass '<PASSWORD>'
            -p '/home/gevorg/Pictures/1.png'
            -p '/home/gevorg/Photos/2.png'
            -p '/home/gevorg/Images/3.png'
            --dest 111222333

    - NOTE 1: Hit 'ENTER' when you are prompted to provide caption and
    description and leave it blank.

    - NOTE 2: In this case each photo name will be used
    as caption and description.

    \b
    \b
    In case of no caption/no description each photo will be uploaded with its
    name as a caption/description. Thus, each one will be uploaded separately,
    and you can follow the process of uploading in terminal/stdout.

    \b
    Once all photos are uploaded successfully, it will display uploaded photos'
    related info table in the terminal/stdout: there will be link to each
    photo's largest copy, that VK stores in storages.

    \b
    \b
    WARNING: for your information, for your security.
    As of 28-Jan-2022 vk stores all uploaded photos to its storages, and they
    are still available after their deletion. It does not matter how you
    uploaded your photos. You can open any of your photo in vk album, click on
    the 'More' drop-down under the bottom-right corner of the photo, select
    'Open original' option, delete that photo, make sure that it is gone from
    that album and from all photos, but the original one still exists - refresh
    that page and make sure that it is the case.
    I guess it is done for users who will be asking for repairing deleted
    photos, but there is no option for users to choose photo deletion
    permanently.

    """

    print()
    display_args_opts(locals())

    print()
    uploading_photos, invalid_paths = check_photos_existence(
        source_folder, photos)
    print_invalid_paths(source_folder, invalid_paths)
    upload_photos(username, password,
                  uploading_photos, vk_album_id,
                  caption, description)


if __name__ == '__main__':
    upload_photos_to_album()
