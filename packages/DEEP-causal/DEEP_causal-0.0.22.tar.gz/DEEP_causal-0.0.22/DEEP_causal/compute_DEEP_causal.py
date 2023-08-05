import pandas as pd
import numpy as np
import math
import time
from gsq.binary import g_square_bin


def compute_dc(
    train_data,
    parents_trtout,
    test_data,
    p_thres=10,
    z_sig_thres=1.96,
    close_CATE=False,
    close_CATE_thres=0.08,
    adjusting=True,
    adjusting_thres=0.05,
    testing=True,
):
    """Main function for DEEP_causal.
    :param train_data: input data
    :param parents_trtout: parents, treatment, outcome
    :param test_data: input data
    :param p_thres: patterns more than p_thres are considered as base patterns
    :param z_sig_thres: gamma = 95%
    :param close_CATE: ignore small CATE difference
    :param close_CATE_thres: threshold for small CATE difference
    :param adjusting: adjusting due to confounders 
    :param adjusting_thres: threshold for adjusting
    :param testing: testing data available
    """

    parents_only = parents_trtout[:-2]
    nPA = len(parents_only)
    treatment = parents_trtout[-2]
    outcome = parents_trtout[-1]

    parents_only_df = train_data[parents_only]
    parents_trtout_df = train_data[parents_trtout]

    # Create specific patterns table
    specific_patterns_df = parents_only_df.drop_duplicates()
    specific_patterns_df = specific_patterns_df.reset_index(drop=True)
    specific_patterns_df["n11"] = 0
    specific_patterns_df["n12"] = 0
    specific_patterns_df["n21"] = 0
    specific_patterns_df["n22"] = 0

    # Find all patterns
    for i in range(len(specific_patterns_df)):

        cases = (
            specific_patterns_df.loc[i, parents_only]
            .to_frame()
            .T.merge(parents_trtout_df)
        )

        specific_patterns_df.loc[i, "n11"] = len(
            cases[(cases[treatment] == 1) & (cases[outcome] == 1)]
        )
        specific_patterns_df.loc[i, "n12"] = len(
            cases[(cases[treatment] == 1) & (cases[outcome] == 0)]
        )
        specific_patterns_df.loc[i, "n21"] = len(
            cases[(cases[treatment] == 0) & (cases[outcome] == 1)]
        )
        specific_patterns_df.loc[i, "n22"] = len(
            cases[(cases[treatment] == 0) & (cases[outcome] == 0)]
        )

    specific_patterns_df["n11"] += 1
    specific_patterns_df["n12"] += 1
    specific_patterns_df["n21"] += 1
    specific_patterns_df["n22"] += 1

    sum(specific_patterns_df["n11"]) + sum(specific_patterns_df["n12"]) + sum(
        specific_patterns_df["n21"]
    ) + sum(specific_patterns_df["n22"])

    # Compute phi
    pi_1 = specific_patterns_df["n11"] / (
        specific_patterns_df["n11"] + specific_patterns_df["n12"]
    )
    pi_2 = specific_patterns_df["n21"] / (
        specific_patterns_df["n21"] + specific_patterns_df["n22"]
    )
    specific_patterns_df["phi"] = pi_1 - pi_2

    # Compute Z
    n1_ = specific_patterns_df["n11"] + specific_patterns_df["n12"]
    n0_ = specific_patterns_df["n21"] + specific_patterns_df["n22"]
    r_bar = (specific_patterns_df["n11"] + specific_patterns_df["n21"]) / (n1_ + n0_)
    specific_patterns_df["Z"] = (
        abs(specific_patterns_df["phi"]) - 0.5 * (1 / n1_ + 1 / n0_)
    ) / (r_bar * (1 - r_bar) * (1 / n1_ + 1 / n0_)).transform("sqrt")

    # Remove patterns that number smaller than 10
    specific_patterns_df["N"] = (
        specific_patterns_df["n11"]
        + specific_patterns_df["n12"]
        + specific_patterns_df["n21"]
        + specific_patterns_df["n22"]
    )
    specific_patterns_df = specific_patterns_df[specific_patterns_df["N"] > 10]
    specific_patterns_df = specific_patterns_df.reset_index(drop=True)

    # Faster method
    new_index = len(specific_patterns_df)
    dist_pair_phi_gap = pd.DataFrame(
        {"p1": [], "p2": [], "dist": [], "pair_phi_gap": [], "Z1": [], "Z2": []}
    )
    first_loop = True
    adjusting = True

    # Prepare for merging
    is_mergable = True
    while is_mergable:
        pairs_to_merge = []

        if first_loop:
            for i in specific_patterns_df.index:
                compare = (
                    specific_patterns_df.loc[i, parents_only]
                    == specific_patterns_df.loc[
                        specific_patterns_df.index > i, parents_only
                    ]
                )
                compare = np.sum(compare, axis=1)

                dist_pair_phi_gap_tmp = pd.DataFrame(
                    {
                        "p1": [],
                        "p2": [],
                        "dist": [],
                        "pair_phi_gap": [],
                        "Z1": [],
                        "Z2": [],
                    }
                )
                dist_pair_phi_gap_tmp.loc[:, "p1"] = np.repeat(i, len(compare))
                dist_pair_phi_gap_tmp.loc[:, "p2"] = compare.index
                dist_pair_phi_gap_tmp.loc[:, "dist"] = compare.values
                dist_pair_phi_gap_tmp.loc[:, "pair_phi_gap"] = abs(
                    specific_patterns_df.loc[i, "phi"]
                    - specific_patterns_df.loc[specific_patterns_df.index > i, "phi"]
                ).values

                dist_pair_phi_gap_tmp.loc[:, "Z1"] = np.repeat(
                    specific_patterns_df.loc[i, "Z"], len(compare)
                )
                dist_pair_phi_gap_tmp.loc[:, "Z2"] = specific_patterns_df.loc[
                    specific_patterns_df.index > i, "Z"
                ].values

                dist_pair_phi_gap = dist_pair_phi_gap.append(
                    dist_pair_phi_gap_tmp
                )  # Add to main df

            first_loop = False

        else:
            compare = (
                specific_patterns_df.loc[max(specific_patterns_df.index), parents_only]
                == specific_patterns_df.loc[
                    specific_patterns_df.index < max(specific_patterns_df.index),
                    parents_only,
                ]
            )
            compare = np.sum(compare, axis=1)

            dist_pair_phi_gap_tmp = pd.DataFrame(
                {"p1": [], "p2": [], "dist": [], "pair_phi_gap": [], "Z1": [], "Z2": []}
            )
            dist_pair_phi_gap_tmp.loc[:, "p1"] = np.repeat(
                max(specific_patterns_df.index), len(compare)
            )
            dist_pair_phi_gap_tmp.loc[:, "p2"] = compare.index
            dist_pair_phi_gap_tmp.loc[:, "dist"] = compare.values
            dist_pair_phi_gap_tmp.loc[:, "pair_phi_gap"] = abs(
                specific_patterns_df.loc[max(specific_patterns_df.index), "phi"]
                - specific_patterns_df.loc[
                    specific_patterns_df.index < max(specific_patterns_df.index), "phi"
                ]
            ).values

            dist_pair_phi_gap_tmp.loc[:, "Z1"] = np.repeat(
                specific_patterns_df.loc[max(specific_patterns_df.index), "Z"],
                len(compare),
            )
            dist_pair_phi_gap_tmp.loc[:, "Z2"] = specific_patterns_df.loc[
                specific_patterns_df.index < max(specific_patterns_df.index), "Z"
            ].values

            dist_pair_phi_gap = dist_pair_phi_gap.append(
                dist_pair_phi_gap_tmp
            )  # Add to main df

        # Remove both significant patterns
        dist_pair_phi_gap = dist_pair_phi_gap.reset_index(drop=True)
        dist_pair_phi_gap = dist_pair_phi_gap.drop(
            dist_pair_phi_gap[
                (dist_pair_phi_gap["Z1"] > z_sig_thres)
                & (dist_pair_phi_gap["Z2"] > z_sig_thres)
            ].index
        )

        # Stop merge when
        if len(dist_pair_phi_gap) == 0:
            is_mergable = False
            continue

        # Get one pair
        pairs_to_merge = dist_pair_phi_gap.sort_values(
            by=["dist", "pair_phi_gap"], ascending=[False, True]
        ).iloc[0, :]

        # print(pairs_to_merge)
        # print("Finished", time.time() - time_start)

        # # Checking Step
        # if (pairs_to_merge_1[0] != pairs_to_merge["p1"] or pairs_to_merge_1[1] != pairs_to_merge["p2"]) and (pairs_to_merge_1[0] != pairs_to_merge["p2"] or pairs_to_merge_1[1] != pairs_to_merge["p1"]):
        #     break

        # Stop merge when
        if len(pairs_to_merge) == 0:
            is_mergable = False
            continue

        # Merging
        p1 = specific_patterns_df.loc[
            pairs_to_merge[0],
        ]
        p2 = specific_patterns_df.loc[
            pairs_to_merge[1],
        ]
        new_pattern = p1.copy(deep=True)  # Initialise new pattern
        for i in range(nPA):
            if pd.isna(p1.iloc[i]) or pd.isna(p2.iloc[i]) or p1.iloc[i] != p2.iloc[i]:
                new_pattern[i] = None

        new_pattern["n11"] = p1["n11"] + p2["n11"]
        new_pattern["n12"] = p1["n12"] + p2["n12"]
        new_pattern["n21"] = p1["n21"] + p2["n21"]
        new_pattern["n22"] = p1["n22"] + p2["n22"]
        new_pattern["N"] = (
            new_pattern["n11"]
            + new_pattern["n12"]
            + new_pattern["n21"]
            + new_pattern["n22"]
        )  # N

        pi_1 = new_pattern["n11"] / (new_pattern["n11"] + new_pattern["n12"])  # phi
        pi_2 = new_pattern["n21"] / (new_pattern["n21"] + new_pattern["n22"])
        new_pattern["phi"] = pi_1 - pi_2

        n1_ = new_pattern["n11"] + new_pattern["n12"]  # Z
        n0_ = new_pattern["n21"] + new_pattern["n22"]
        r_bar = (new_pattern["n11"] + new_pattern["n21"]) / (n1_ + n0_)
        new_pattern["Z"] = (
            abs(new_pattern["phi"]) - 0.5 * (1 / n1_ + 1 / n0_)
        ) / math.sqrt(r_bar * (1 - r_bar) * (1 / n1_ + 1 / n0_))

        # Remove old patterns
        if p1["Z"] < z_sig_thres:
            specific_patterns_df = specific_patterns_df.drop(pairs_to_merge[0])
            dist_pair_phi_gap = dist_pair_phi_gap.drop(
                dist_pair_phi_gap[
                    (dist_pair_phi_gap["p1"] == pairs_to_merge[0])
                    | (dist_pair_phi_gap["p2"] == pairs_to_merge[0])
                ].index
            )
        if p2["Z"] < z_sig_thres:
            specific_patterns_df = specific_patterns_df.drop(pairs_to_merge[1])
            dist_pair_phi_gap = dist_pair_phi_gap.drop(
                dist_pair_phi_gap[
                    (dist_pair_phi_gap["p1"] == pairs_to_merge[1])
                    | (dist_pair_phi_gap["p2"] == pairs_to_merge[1])
                ].index
            )

        # Add new pattern
        new_pattern = new_pattern.rename(new_index)
        new_index += 1
        specific_patterns_df = specific_patterns_df.append(new_pattern)

        # Reset index
        # specific_patterns_df = specific_patterns_df.reset_index(drop=True)

        # print(new_pattern)

    if adjusting:
        # Adjusting due to independence
        # gsq.gSquareBin(x, y, S, dm, verbose = FALSE, adaptDF = FALSE)
        # from gsq import gsq_testdata
        # dm = np.array([gsq_testdata.bin_data]).reshape((5000,5))
        # g_square_bin(dm, 0, 1, set([]))
        # g_square_bin(dm, 0, 2, set([]))

        # Independence test
        var_idx = [train_data.columns.get_loc(p) for p in parents_only]
        treatment_idx = train_data.columns.get_loc(treatment)
        var_ind = [
            g_square_bin(np.array(train_data), v, treatment_idx, set([]))
            for v in var_idx
        ]
        var_ad_names = np.array(parents_only)[np.array(var_ind) < adjusting_thres]
        var_un_names = np.array(parents_only)[np.array(var_ind) >= adjusting_thres]

        # Select patterns to be adjusted
        target_list = specific_patterns_df[var_ad_names].isnull()
        target_list = np.sum(target_list, axis=1)
        adjust_list = specific_patterns_df.loc[target_list[target_list > 0].index, :]
        unadjust_list = specific_patterns_df.loc[target_list[target_list == 0].index, :]

        # Adjusting
        adjusted_list = pd.DataFrame(columns=adjust_list.columns)
        for i in adjust_list.index:
            # print(i)
            this_pattern_ad = pd.DataFrame(columns=adjust_list.columns)
            this_pattern = adjust_list.loc[i,][parents_only]
            this_pattern_noNAN = this_pattern[this_pattern.notnull()]

            this_pattern_covered_idx = np.sum(
                train_data[this_pattern_noNAN.index] == this_pattern_noNAN, axis=1
            )
            this_pattern_covered_idx = this_pattern_covered_idx[
                this_pattern_covered_idx == len(this_pattern_noNAN)
            ]
            this_pattern_covered = train_data.loc[this_pattern_covered_idx.index, :]

            this_pattern_ad = this_pattern_ad.append(adjust_list.loc[i,][parents_only])

            this_pattern_ad["n11"] = len(
                this_pattern_covered[
                    (this_pattern_covered[treatment] == 1)
                    & (this_pattern_covered[outcome] == 1)
                ]
            )
            this_pattern_ad["n12"] = len(
                this_pattern_covered[
                    (this_pattern_covered[treatment] == 1)
                    & (this_pattern_covered[outcome] == 0)
                ]
            )
            this_pattern_ad["n21"] = len(
                this_pattern_covered[
                    (this_pattern_covered[treatment] == 0)
                    & (this_pattern_covered[outcome] == 1)
                ]
            )
            this_pattern_ad["n22"] = len(
                this_pattern_covered[
                    (this_pattern_covered[treatment] == 0)
                    & (this_pattern_covered[outcome] == 0)
                ]
            )

            # Compute phi
            pi_1 = this_pattern_ad["n11"] / (
                this_pattern_ad["n11"] + this_pattern_ad["n12"]
            )
            pi_2 = this_pattern_ad["n21"] / (
                this_pattern_ad["n21"] + this_pattern_ad["n22"]
            )
            this_pattern_ad["phi"] = pi_1 - pi_2

            # Compute Z
            n1_ = this_pattern_ad["n11"] + this_pattern_ad["n12"]
            n0_ = this_pattern_ad["n21"] + this_pattern_ad["n22"]
            r_bar = (this_pattern_ad["n11"] + this_pattern_ad["n21"]) / (n1_ + n0_)
            this_pattern_ad["Z"] = (
                abs(this_pattern_ad["phi"]) - 0.5 * (1 / n1_ + 1 / n0_)
            ) / (r_bar * (1 - r_bar) * (1 / n1_ + 1 / n0_)).transform("sqrt")

            this_pattern_ad["N"] = (
                this_pattern_ad["n11"]
                + this_pattern_ad["n12"]
                + this_pattern_ad["n21"]
                + this_pattern_ad["n22"]
            )

            adjusted_list = adjusted_list.append(this_pattern_ad)

            # print(
            #     adjust_list.loc[i,]
            # )
            # print(this_pattern_ad)

        specific_patterns_df_old = specific_patterns_df
        specific_patterns_df = unadjust_list.append(adjusted_list)

    # Sort by NA a, phi d, NN d
    for i in specific_patterns_df.index:
        specific_patterns_df.loc[i, "nNA"] = (
            specific_patterns_df.loc[i, parents_only].isna().values.sum()
        )

    specific_patterns_df = specific_patterns_df.sort_values(
        by=["nNA", "phi", "N"], ascending=[True, False, False]
    )
    specific_patterns_df = specific_patterns_df.reset_index(drop=True)
    specific_patterns_df_copy = specific_patterns_df.copy()

    # ==================================================================================================================================
    # Testing
    # ==================================================================================================================================
    if testing:
        data_test = test_data
        data_test = data_test.drop(labels=["Unnamed: 0"], axis=1)
        data_test = data_test[parents_trtout]
        data_test["CATE"] = 0

        specific_patterns_df = specific_patterns_df.drop(
            ["Z", "N", "nNA", "n11", "n12", "n21", "n22"], axis=1
        )
        specific_patterns_df["n11"] = 0
        specific_patterns_df["n12"] = 0
        specific_patterns_df["n21"] = 0
        specific_patterns_df["n22"] = 0

        for i in range(len(data_test)):
            for j in range(len(specific_patterns_df)):

                test_pattern = data_test.loc[i, parents_only]
                result_pattern = specific_patterns_df.loc[j, parents_only]

                pattern_matched = False
                for k in range(nPA):
                    if (
                        pd.isna(test_pattern.iloc[k])
                        or pd.isna(result_pattern.iloc[k])
                        or test_pattern.iloc[k] == result_pattern.iloc[k]
                    ):
                        pattern_matched = True
                    else:
                        pattern_matched = False
                        break

                if pattern_matched:
                    if (
                        data_test.loc[i, treatment] == 1
                        and data_test.loc[i, outcome] == 1
                    ):
                        specific_patterns_df.loc[j, "n11"] = (
                            specific_patterns_df.loc[j, "n11"] + 1
                        )
                    elif (
                        data_test.loc[i, treatment] == 1
                        and data_test.loc[i, outcome] == 0
                    ):
                        specific_patterns_df.loc[j, "n12"] = (
                            specific_patterns_df.loc[j, "n12"] + 1
                        )
                    elif (
                        data_test.loc[i, treatment] == 0
                        and data_test.loc[i, outcome] == 1
                    ):
                        specific_patterns_df.loc[j, "n21"] = (
                            specific_patterns_df.loc[j, "n21"] + 1
                        )
                    elif (
                        data_test.loc[i, treatment] == 0
                        and data_test.loc[i, outcome] == 0
                    ):
                        specific_patterns_df.loc[j, "n22"] = (
                            specific_patterns_df.loc[j, "n22"] + 1
                        )

                    data_test.loc[i, "CATE"] = specific_patterns_df.loc[j, "phi"]
                    # print(test_pattern, result_pattern)
                    # print("i:", len(data_test), i, "j", len(specific_patterns_df), j)
                    break

        # Evaluate predictions
        data_test = data_test.sort_values(by="CATE", ascending=False)
        data_test_final = data_test.reset_index(drop=True)
        data_test_final["Decile_rank"] = pd.qcut(
            data_test_final.index, 10, labels=False, duplicates="drop"
        )

        decile_values = []

        for i in range(10):
            current_decile = data_test_final[data_test_final["Decile_rank"] == i]
            n11 = len(
                current_decile[
                    (current_decile[treatment] == 1) & (current_decile[outcome] == 1)
                ]
            )
            n12 = len(
                current_decile[
                    (current_decile[treatment] == 1) & (current_decile[outcome] == 0)
                ]
            )
            n21 = len(
                current_decile[
                    (current_decile[treatment] == 0) & (current_decile[outcome] == 1)
                ]
            )
            n22 = len(
                current_decile[
                    (current_decile[treatment] == 0) & (current_decile[outcome] == 0)
                ]
            )

            pi_1 = n11 / (n11 + n12)
            pi_2 = n21 / (n21 + n22)
            phi = pi_1 - pi_2
            decile_values.append(phi)

        # Plot results
        decile_values_df = pd.DataFrame(decile_values)
        ax = decile_values_df.plot.bar(rot=0)

        specific_patterns_df = specific_patterns_df.rename(columns={"phi": "est_CATE"})

    return specific_patterns_df_copy, specific_patterns_df

