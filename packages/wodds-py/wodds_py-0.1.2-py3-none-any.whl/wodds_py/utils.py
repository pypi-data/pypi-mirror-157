import numpy as np
import re
from scipy.stats import norm

def wodd_format_s_fix(wodd_name):
    """make substitutions of improper wodd names "S0" and "S1"

    Args:
        wodd_name (string): "S0", "S1", "M". etc

    Example:
        assert wodd_format_s_fix("S1") == "S"
    """
    if isinstance(wodd_name, str):
        wodd_name = re.sub("S0", "", wodd_name)
        wodd_name = re.sub("S1", "S", wodd_name)
        return wodd_name
    else:
      raise "wodd_name must be a string"

def raw_wodd(d: int):
    """make the wodd name string

    Args:
        index (int): depth level of wodd

    Returns:
        str: wodd name string
    
    Example:
        assert raw_wodd(10) == "S2F"
    """
    try:
        d
        int_part = 2**d
        power = 0
        counted = False
        if (int_part >= 16):
            while (counted == False):
                if (int_part >= 16**power):
                    power = power + 1
                else:
                    counted = True
                    power = power - 1
        if 16**(power) * 1 == int_part:
            return wodd_format_s_fix(f"S{power}")
        elif 16**(power) * 2 == int_part:
            return wodd_format_s_fix(f"S{power}M")
        elif 16**(power) * 4 == int_part:
            return wodd_format_s_fix(f"S{power}F")
        elif 16**(power) * 8 == int_part:
            return wodd_format_s_fix(f"S{power}E")
    except ValueError:
        raise "index must be an integer"

def make_wodd_name(index):
    """make the wodd name

    Args:
        index (index): int

    Example: 
        assert make_wodd_name(3) == ['M', 'F', 'E']
    """
    if isinstance(index, int):
        wodd_depth = np.linspace(start=1, stop=index, num=index)
        wodd_name = list(map(raw_wodd, wodd_depth))
        return wodd_name
    else:
        raise "index must be an integer"


def get_wodd_quantiles(y: np.array, alpha: float = 0.05):
    """
    Given the array of data and an alpha value, return the sorted
    array of quantiles to calculate on the data
    """
    y_sorted = np.sort(y)
    n = len(y_sorted)
    alpha = alpha
    # rule 3
    k = get_depth_from_n(int(n), alpha) # depth
    lvl = (k) * 2
    nq = lvl -1
    qs = np.repeat(0.0, nq).astype(float)
    fn = f(n)
    for i in range(1, k+1):
        if i == 1:
          """
          median calculation
          """
          d = f(n)
          qs[i - 1] = 0.5
          d
        else:
          d = f(d)
          if np.ceil(d) != np.floor(d):
              l_idx1 = int(np.floor(d))
              l_idx2 = int(np.ceil(d))
              u_idx1 = int(np.floor(n - d + 1))
              u_idx2 = int(np.ceil(n - d + 1))
              l = np.average([y_sorted[l_idx1], y_sorted[l_idx2]])
              u = np.average([y_sorted[u_idx1], y_sorted[u_idx2]])
              ql = np.average([l_idx1 / n, l_idx2 / n])
              qu = np.average([u_idx1 / n, u_idx2 / n])
          else:
              ql = int(d) / n
              qu = int(np.floor(n - d + 1)) / n
          lower_upper = [ql, qu]
          lower_upper_index = [int(((i - 1) * 2) - 1), int((i - 1) * 2)]
          np.put(qs, lower_upper_index, lower_upper)
    return qs



def select_wodd_name_from_table(index):
    """define all the wodds in a table. These will be sufficient for even the largest sample sizes

    Args:
        index (int): int
    """
    if isinstance(index, int):
        if (index > 100):
            raise "depth > 100 which is larger than precalculated table of wodd names"
        else:
            first_100_wodds = [
            "M", "F", "E", "S", "SM",
            "SF", "SE", "S2", "S2M", "S2F", "S2E", "S3", "S3M", "S3F", "S3E",
            "S4", "S4M", "S4F", "S4E", "S5", "S5M", "S5F", "S5E", "S6", "S6M",
            "S6F", "S6E", "S7", "S7M", "S7F", "S7E", "S8", "S8M", "S8F",
            "S8E", "S9", "S9M", "S9F", "S9E", "S0", "S0M", "S0F", "S0E",
            "S1", "S1M", "S1F", "S1E", "S2", "S2M", "S2F", "S2E", "S3", "S3M",
            "S3F", "S3E", "S4", "S4M", "S4F", "S4E", "S5", "S5M", "S5F",
            "S5E", "S6", "S6M", "S6F", "S6E", "S7", "S7M", "S7F", "S7E",
            "S8", "S8M", "S8F", "S8E", "S9", "S9M", "S9F", "S9E", "S20",
            "S20M", "S20F", "S20E", "S21", "S21M", "S21F", "S21E", "S22",
            "S22M", "S22F", "S22E", "S23", "S23M", "S23F", "S23E", "S24",
            "S24M", "S24F", "S24E", "S25"
            ]
            return first_100_wodds[0:index]
    else:
        raise "index must be an integer"

def get_n_from_depth(d, alpha = 0.05, conservative = True):
    """Get sample size from depth: Calculates the sample size needed given an alpha level and depth

    Args:
        d (int): an integer depth
        alpha (float, optional): alpha level such as 0.1, 0.05, 0.01. An alpha of 0.05 would be associated with a 95 percent confidence interval. Defaults to 0.05.
        conservative (bool, optional): If TRUE then a conservative (larger) sample size is returned. Defaults to True.

    Returns:
        float: sample size
    
    Example:
    ```
        get_n_from_depth(7, 0.01)
    ```
    """
    if isinstance(d, int) == False:
        raise "d (depth) must be an integer"
    else:
        print("hiasdfhias")
        if conservative == False:
            sample_size = 2**((d-1) + np.log2(2 * (norm.ppf(1 - (alpha / 2))**2)))
            return np.floor(sample_size) # a simple round down of the decimals # not necessary just convenience
        else:
            sample_size = 2**((d) + np.log2(2 * (norm.ppf(1 - (alpha / 2))**2)))
            return np.floor(sample_size) # a simple round down of the decimals # not necessary just convenience

def get_depth_from_n(n, alpha = 0.05):
    """Get depth from sample size

    Args:
        n (int): n an integer scalar sample size
        alpha (float, optional): alpha level such as 0.1, 0.05, 0.01. An alpha of 0.05 would be associated with a 95 percent confidence interval. Defaults to 0.05. 

    Returns:
        int: an integer depth

    Example:
    ```
        get_depth_from_n(1000, 0.05)
    ```
    """
    if isinstance(n, int):
        #stopifnot(is.numeric(alpha) && length(alpha) == 1)
        #stopifnot(alpha > 0 && alpha < 1)
        k = int(np.floor(np.log2(n) - np.log2(2 * (norm.ppf(1 - (alpha / 2))**2))) + 1)
        return k
    else:
        raise "n must be an integer. Here is an example get_depth_from_n(n=1e4L, 0.05). suffix the number with L to force value to be an integer"

def f(n):
    return (1 + np.floor(n)) / 2

def make_outlier_name(o_max_len):
    """Make outlier names, such as O1, O2, O3, ...

    Args:
        o_max_len (int): how many Os are needed

    Returns:
        np.array(str): array of Os ["O1", "O2", ...]
    """
    outlier_array = (np.linspace(start = 1, stop = o_max_len, num=o_max_len)).astype(int)
    outlier_array_string = outlier_array.astype(str)
    prefix_outlier = list(map(lambda x: "O"+x, outlier_array_string))
    return prefix_outlier

class WoddData:
    """
    There are a many parts needed for a whisker odds table. This
    returns data needed for any additional tables.

    Args:
        y (np.array): vector of data
        alpha (float, optional): confidence level. Defaults to 0.05.

    Returns:
        `lower (np.array, float)`: lower wodd values
        `wodd_depth_name (np.array, string)`: name associated with the values
        `upper (np.array, float)`: upper wodd values
        `array_o_lower (np.array, float)`: outlier lower values
        `o_name (np.array, string)`: outlier wodd names
        `array_o_upper (np.array, float)`: outlier upper values
        `o_max_len (int)`: the max length between the upper and lower outlier arrays
        `depth (int)`: depth level 
        `tail_area (np.array(), int)`: area in the tail i.e. [2, 4, 8, 16, 32, ...] 
        `array_qs (np.array, float)`: array of quantiles (both upper and lower)
        `vf (np.array, float)`: array of values (both upper and lower)
        `qlower (np.array, float)`: array of quantiles (just the lower quantiles)
        `qupper (np.array, float)`: array of quantiles (just the upper quantiles)

    Example:
    ```
        from numpy.random import MT19937, RandomState, SeedSequence, normal
        from wodds_py.utils import WoddData
        import pandas as pd
        rs = RandomState(MT19937(SeedSequence(42)))
        y = rs.normal(loc=0, scale=1, size = 10000)
        y = pd.read_csv("../../../code/r/y.csv").y
        wd= WoddData(y)
        df_wodds = pd.DataFrame({"lower": wd.lower, "wodd_depth_name": wd.wodd_depth_name, "upper": wd.upper,})
        print(df_wodds)
    ```
    """
    def __init__(self, y, alpha = 0.05):
        array_qs = get_wodd_quantiles(y, alpha = alpha)
        vf = np.quantile(y, array_qs)
        vf = np.hstack((np.median(y),vf)) # concatonate extra median to list
        qlower = array_qs[0::2]
        qupper = array_qs[1::2]
        lower = vf[0::2]
        upper = vf[1::2]
        k = get_depth_from_n(int(len(y)), 0.05)
        depth = np.linspace(start = 1, stop = k, num = k)
        tail_area = 2 ** depth
        wodd_depth_name = select_wodd_name_from_table(k)
        o_upper = np.sort(y[y > np.max(upper)])
        o_lower = np.sort(y[y < np.min(lower)])[::-1] #, decreasing = True
        o_max_len = np.max([len(o_upper), len(o_lower)])
        o_name = make_outlier_name(o_max_len)
        array_o_lower = np.repeat(0.0, o_max_len).astype(float) * np.nan
        array_o_upper = np.repeat(0.0, o_max_len).astype(float) * np.nan
        np.put(array_o_upper, np.arange(0, len(o_upper), 1, dtype=int), o_upper)
        np.put(array_o_lower, np.arange(0, len(o_lower), 1, dtype=int), o_lower)
        self.array_lower = lower
        self.wodd_depth_name = wodd_depth_name
        self.array_upper = upper
        self.array_o_lower = array_o_lower
        self.o_name = o_name
        self.array_o_upper = array_o_upper
        self.o_max_len = o_max_len
        self.depth = depth
        self.tail_area = tail_area
        self.array_qs = array_qs
        self.vf = vf
        self.qlower = qlower
        self.qupper = qupper