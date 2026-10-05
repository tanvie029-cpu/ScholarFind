document.addEventListener("DOMContentLoaded", function () {


    // =====================================================
    // ELEMENTS
    // =====================================================

    const form =
        document.getElementById("search-form");

    const searchInput =
        document.querySelector(
            'input[name="query"]'
        );

    const searchButton =
        document.querySelector(
            ".search-button"
        );

    const clearFilters =
        document.getElementById(
            "clear-filters"
        );

    const emptyReset =
        document.getElementById(
            "empty-reset"
        );

    const results =
        document.getElementById(
            "results"
        );


    // =====================================================
    // SEARCH LOADING STATE
    // =====================================================

    if (form && searchButton) {

        form.addEventListener(
            "submit",
            function () {

                searchButton.disabled = true;

                const text =
                    searchButton.querySelector(
                        "span:first-child"
                    );

                const arrow =
                    searchButton.querySelector(
                        ".button-arrow"
                    );

                if (text) {
                    text.textContent =
                        "Searching";
                }

                if (arrow) {
                    arrow.textContent =
                        "…";
                }

            }
        );

    }


    // =====================================================
    // SCORE BARS
    // =====================================================

    document
        .querySelectorAll(".score-fill")
        .forEach(function (bar) {

            const score =
                parseFloat(
                    bar.dataset.score
                ) || 0;

            const safeScore =
                Math.min(
                    100,
                    Math.max(
                        0,
                        score
                    )
                );

            setTimeout(function () {

                bar.style.width =
                    safeScore + "%";

            }, 150);

        });


    // =====================================================
    // CLEAR FILTERS
    // =====================================================

    if (
        clearFilters &&
        form
    ) {

        clearFilters.addEventListener(
            "click",
            function () {

                form
                    .querySelectorAll("select")
                    .forEach(function (select) {

                        select.value = "";

                        select.classList.remove(
                            "changed"
                        );

                    });

            }
        );

    }


    // =====================================================
    // RESET SEARCH
    // =====================================================

    if (
        emptyReset &&
        form
    ) {

        emptyReset.addEventListener(
            "click",
            function () {

                if (searchInput) {

                    searchInput.value = "";

                }


                form
                    .querySelectorAll("select")
                    .forEach(function (select) {

                        select.value = "";

                    });


                form.submit();

            }
        );

    }


    // =====================================================
    // POPULAR SEARCH BUTTONS
    // =====================================================

    document
        .querySelectorAll(
            "[data-search]"
        )
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    if (
                        !searchInput ||
                        !form
                    ) {
                        return;
                    }


                    searchInput.value =
                        button.dataset.search;


                    form
                        .querySelectorAll("select")
                        .forEach(function (select) {

                            select.value = "";

                        });


                    form.submit();

                }
            );

        });


    // =====================================================
    // SCROLL TO RESULTS
    // =====================================================

    if (results) {

        setTimeout(
            function () {

                results.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            },
            200
        );

    }


    // =====================================================
    // FILTER CHANGE EFFECT
    // =====================================================

    document
        .querySelectorAll(
            ".filter-field select"
        )
        .forEach(function (select) {

            select.addEventListener(
                "change",
                function () {

                    if (this.value !== "") {

                        this.classList.add(
                            "changed"
                        );

                    } else {

                        this.classList.remove(
                            "changed"
                        );

                    }

                }
            );

        });

});