<a name="readme-top"></a>



<!-- PROJECT SHIELDS -->
<div align="center">

  <a href="[contributors-url]">[![Contributors][contributors-shield]][contributors-url]</a>
  <a href="[forks-url]">[![Forks][forks-shield]][forks-url]</a>
  <a href="[stars-url]">[![Stargazers][stars-shield]][stars-url]</a>
  <a href="[issues-url]">[![Issues][issues-shield]][issues-url]</a>
  <a href="[license-url]">[![BSD-3-Clause License][license-shield]][license-url]</a>

</div>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">EduTecX</h3>

  <p align="center">
    Paving sustainable education pathways
    <br />
    <a href="https://github.com/caffeine-addictt/edutecx/issues">Report Bug</a>
    ·
    <a href="https://edutecx.ngjx.org">Live Demo</a>
  </p>
</div>



<!-- ABOUT THE PROJECT -->
## About The Project
> Application Development project @ Nanyang Polytechnic Singapore

This project aims to provide more environmental-friendly education materials.
By bridging the gap between vendors, educators and students, we aim to make the learning process more sustainable and accessible.

To saving children's backs!

<br />

> ![WARNING]
> This project will not be maintained after 12/02/2024. However, issues and pull requests will still be accepted.

<br />

Live the live demo [here](https://edutecx.ngjx.org).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may set up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

* Python 3.11.2+

### Installation

_Below is an example of how you can install and set up your app._

1. Clone the repository
   ```sh
   git clone https://github.com/caffeine-addictt/edutecx
   cd edutecx
   ```
2. Install dependencies
   ```sh
   pip install -r requirements.txt
   ```
3. Write environment variables
   ```sh
   echo "ENV=development" >> .env
   ```
4. Start the server
   ```sh
   gunicorn --bind 0.0.0.0:8080 --workers=2 --threads=2 --worker-class=gthread --reload run:app
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Release

See the [open issues](https://github.com/caffeine-addictt/edutecx/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**. ( ˶ˆᗜˆ˵ )

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the GNU GENERAL PUBLIC LICENSE. See [`LICENSE`](./LICENSE) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

- Alex - contact@edutecx.ngjx.org
- Project Link: [https://github.com/caffeine-addictt/edutecx](https://github.com/caffeine-addictt/edutecx)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/caffeine-addictt/edutecx.svg?style=for-the-badge
[contributors-url]: https://github.com/caffeine-addictt/edutecx/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/caffeine-addictt/edutecx.svg?style=for-the-badge
[forks-url]: https://github.com/caffeine-addictt/edutecx/network/members
[stars-shield]: https://img.shields.io/github/stars/caffeine-addictt/edutecx.svg?style=for-the-badge
[stars-url]: https://github.com/caffeine-addictt/edutecx/stargazers
[issues-shield]: https://img.shields.io/github/issues/caffeine-addictt/edutecx.svg?style=for-the-badge
[issues-url]: https://github.com/caffeine-addictt/edutecx/issues
[license-shield]: https://img.shields.io/github/license/caffeine-addictt/edutecx.svg?style=for-the-badge
[license-url]: https://github.com/caffeine-addictt/edutecx/blob/master/LICENSE
