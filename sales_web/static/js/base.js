document.addEventListener(
    "DOMContentLoaded",
    function () {

        const currentPath =
            window.location.pathname;


        const navItems =
            document.querySelectorAll(
                ".nav-item"
            );


        navItems.forEach(
            function (item) {

                const href =
                    item.getAttribute(
                        "href"
                    );


                if (
                    href &&
                    href !== "/" &&
                    currentPath.startsWith(
                        href
                    )
                ) {

                    item.classList.add(
                        "active"
                    );

                }

            }
        );

    }
);