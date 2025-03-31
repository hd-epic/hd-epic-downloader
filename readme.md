# The HD-EPIC downloader

We provide a `python` script to download the [HD-EPIC Dataset](https://hd-epic.github.io/), either in 
its entirety or in parts (e.g. only VRS files). You can also download data for a subset of participants. 

### Python version and libraries

The script requires Python **3.5+** and  **no external libraries**. However, the script will use **tqdm** if it
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
python hd-epic-downloader ${output-path}
```

Where `${output-path}` is the path where you want to download the dataset. Note that the script will create a 
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

If you want to download only videos, then:

```bash
python hd-epic-downloader.py /home/data --videos
```

Note that these arguments can be **combined** to download multiple things. For example:

```bash
python hd-epic-downloader.py ---videos --vrs
```

Will download both videos and VRS files. 

### Specifying participants

You can use the argument `--participants` if you want to download data for only a subset of the participants. 
Participants must be specified with a number ranging between 1 and 9, e.g. `--participants 1,2,3`

This argument can also be combined with the aforementioned arguments. For example:

```bash
python hd-epic-downloader.py --videos --participants 1,2,3
```

Will download only videos from `P01, P02` and `P03`.
