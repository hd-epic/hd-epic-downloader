# The HD-EPIC downloader

We provide a `python` script to download the [HD-EPIC Dataset](https://hd-epic.github.io/), either in 
its entirety or in parts (e.g. only VRS files). You can also download data for a subset of participants. 

### Python version and libraries

The script requires Python **3.6+** and  **no external libraries**. However, the script will use **tqdm** if it
is detected in your environment to display progress bars and estimate download time. 
Although optional, we recommend [installing tqdm](https://tqdm.github.io) for the best experience.

### Data size and resuming downloads

In total the dataset size is 2.3 TB split as follows:

| Data          | Size     |
|:--------------|:---------|
| Videos        | 115.5 GB |
| VRS           | 1.9 TB   | 
| Digital twin  | 1.35 GB  |
| Slam and gaze | 349 GB   |
| Audio HDF5    | 27 GB    |
| Hands masks   | 1.95 GB  |

Previously fully downloaded files will be skipped, so you can download large batches of files over multiple runs.
Make sure you specify the same output path when running the script to resume previous downloads.  

### Download speed

Download speed might be (very) slow depending on the region.  

# Using the script

Clone this repository and `cd` into the repository root folder. Then run the script as follows:

```bash
python hd-epic-downloader.py ${output-path}
```

Where `${output-path}` is the path where you want to download the dataset. The script will create a 
folder named `HD-EPIC` under the path you specify.

The script accepts a number of arguments that allow you to specify what you want to download. 
By default the script will download **everything**. 

You can run `python hd-epic-downloader.py -h` to see the script usage.

### Download only certain data types

If you want to download only subsets of the dataset, you can do so with the following self-explanatory arguments:

| Arg                         | Size     |
|:----------------------------|:---------|
| `--videos`                  | 115.5 GB |
| `--vrs`                     | 1.9 TB   | 
| `--digital-twin`            | 1.35 GB  |
| `--slam-gaze`               | 349 GB   |
| `--audio`                   | 27 GB    |
| `--hands`                   | 1.95 GB  |
| `--consent-form`            | 80KB     | 
| `--acquisition-guidelines`  | 70KB     | 

For example, if you only want to download videos, then:

```bash
python hd-epic-downloader.py /home/data --videos
```

These arguments can be **combined** to download multiple things. For example:

```bash
python hd-epic-downloader.py /home/data --videos --vrs
```

Will only download videos and VRS files. 

### Specifying participants

You can use the argument `--participants` if you want to download data for only a subset of the participants. 
Participants must be specified with a number ranging between 1 and 9, e.g. `--participants 1,2,3`

This argument can also be combined with the aforementioned arguments. For example:

```bash
python hd-epic-downloader.py /home/data --videos --participants 1,2,3
```

Will only download videos from `P01, P02` and `P03`.

Note that only some data types are organised per participants. 
When using the `--participants` argument the script will only download files organised per participant.
Check the table below to see what is organised per participant and downloaded when using `--participants`.

| Data          | Downloaded with `--participants` |
|:--------------|:---------------------------------|
| Videos        | Yes                              |
| VRS           | Yes                              | 
| Digital twin  | No                               |
| Slam and gaze | Yes                              |
| Audio HDF5    | Yes                              |
| Hands masks   | No                               |

### Specifying video IDs

You can use the argument `--video-id` if you want to download data for specific video IDs. 
Video IDs must be comma-separated strings with the following format: `P0X-2024XXXX-XXXXXX`.
This will download the specified data types (everything by default) only for the specified videos. 

Note that this argument cannot be used in combination with `--participants`, but it can be used with the data type 
arguments to download only specific data types for specific videos. 
For example:

```bash
python hd-epic-downloader.py /home/data --vrs --video-id P01-20240202-110250,P03-20240216-084005,P07-20240529-102652
```

Will only download the VRS files for the videos `P01-20240202-110250,P03-20240216-084005,P07-20240529-102652`.

Note that only some data types are organised per video. 
When using the `--video-id` argument the script will only download files organised per video.
Check the table below to see what is organised per video and downloaded when using `--video-id`.

| Data          | Downloaded with `--video-id` |
|:--------------|:-----------------------------|
| Videos        | Yes                          |
| VRS           | Yes                          | 
| Digital twin  | No                           |
| Slam and gaze | Gaze only                    |
| Audio HDF5    | No                           |
| Hands masks   | No                           |