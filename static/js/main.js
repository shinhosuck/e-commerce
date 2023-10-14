// scroll to top and bottom
const scrollBtns = document.querySelector('.scroll-btns')
const scrollDown = document.querySelector('.scroll-down')
const scrollUp = document.querySelector('.scroll-up')
const bodyWidth = document.querySelector('body')

// mobile navigation
const mobileNavs = [...document.querySelectorAll('.mobile-nav')]
const mobileNavLinks = document.querySelector('.mobile-nav-links')
const mobileNavCloseBtn = document.querySelector('.mobile-nav-close-btn')
const mobileToggleNavBtn = document.querySelector('.mobile-toggle-nav-btn')
const mobileNavBackgroundLayout = document.querySelector('.mobile-nav-background-layout')
const mobileNavLinkSearchButton = document.querySelector('.mobile-nav-link-search-button')

// search form
const navLinkSearchButton = document.querySelector('.nav-link-search-button')
const searchIcon = document.querySelector('.search-icon')
const searchFormWrapper = document.querySelector('.search-form-wrapper')
const searchFormCloseButton = document.querySelector('.search-form-close-btn')
const mobileSearchFormContainer = document.querySelector('.mobile-search-form-container')

// user drop-down menu navigation bar
const toggleUserNavbar = document.querySelector('.toggle-user-navbar')
const loggedInUserNavLinks = document.querySelector('.logged-in-user-nav-links')
const loggedInNavbarArrowUp = document.querySelector('.logged-in-navbar-arrow-up')
const loggedInNavbarArrowDown = document.querySelector('.logged-in-navbar-arrow-down')
const loggedInNavbarUsername = document.querySelector('.logged-in-navbar-username')
const loggedInNavbarUserProfileImg = document.querySelector('.logged-in-navbar-user-profile-img')

// banner image to right and to left buttons
const bannerImgContainers = [...document.querySelectorAll('.banner-img-container')]
const bannerArrowLeft = document.querySelector('.banner-arrow-left')
const bannerArrowRight = document.querySelector('.banner-arrow-right')
const TranslateBtns = [...document.querySelectorAll('.translate-btn')]
const circles = [...document.querySelectorAll('.circle')]

// product detail and description on product detail page
const productDetailToggleBtns = [...document.querySelectorAll('.product-detail-toggle-btn')]
const productDescription = document.querySelector('.product-description')
const productDetail = document.querySelector('.product-detail')
const productDescriptionArrowUp = document.querySelector('.product-description-arrow-up')
const productDescriptionArrowDown = document.querySelector('.product-description-arrow-down')
const productDetailArrowUp = document.querySelector('.product-detail-arrow-up')
const productDetailArrowDown = document.querySelector('.product-detail-arrow-down')
const productDetailExtraImage = [...document.querySelectorAll('.product-detail-extra-image')]

// product likes rating stars
// const productLikeContainer = document.querySelectorAll('.product-like-container')





const body = document.querySelector('body')

/*
==================
SCROLL UP AND DOWN
==================
*/ 
if(scrollDown && scrollUp) {
    if((window.innerWidth - bodyWidth.clientWidth)/2 != 0) {
        scrollBtns.style.right = `${(window.innerWidth - bodyWidth.clientWidth)/2}px`
    }
}


if(scrollDown && scrollUp) {
    window.addEventListener('scroll', (e) => {
        if(window.pageYOffset === 0) {
            scrollDown.style.display = 'none'
            scrollUp.style.display = 'none'
        }
        else if(window.pageYOffset >= 300) {
            scrollDown.style.display = 'none'
            scrollUp.style.display = 'flex'
        }else if(window.pageYOffset <= 300 && window.pageYOffset > 0) {
            scrollDown.style.display = 'flex'
            scrollUp.style.display = 'none'
        }
    })

    window.addEventListener('resize', (e) => {
        if((window.innerWidth - bodyWidth.clientWidth)/2 != 0) {
            scrollBtns.style.right = `${(window.innerWidth - bodyWidth.clientWidth)/2}px`
        }
    })
}



/*
================
MOBILE NAV LINKS
================
*/ 

mobileToggleNavBtn.addEventListener('click', (e) => {
    searchFormWrapper.classList.remove('show-search-form-wrapper')
    mobileNavLinks.classList.add('show-mobile-nav-bar')
    mobileNavBackgroundLayout.style.display = 'block'
    body.style.overflow = 'hidden'

})

mobileNavCloseBtn.addEventListener('click', () => {
    mobileNavLinks.classList.remove('show-mobile-nav-bar')
    mobileNavBackgroundLayout.style.display = 'none'
    body.style.overflow = 'auto'
})

mobileNavs.forEach((nav) => {
    nav.addEventListener('click', (e) => {
        body.style.overflow = 'auto'
    })
})


/*
================
DESKTOP NAV LINKS
================
*/ 

if (toggleUserNavbar) {
    toggleUserNavbar.addEventListener('click', (e) => {
        searchFormWrapper.classList.remove('show-search-form-wrapper')
        loggedInUserNavLinks.classList.toggle('show-logged-in-user-nav-links')
        if(loggedInUserNavLinks.classList.contains('show-logged-in-user-nav-links')){
            loggedInNavbarArrowUp.style.display = 'flex'
            loggedInNavbarArrowDown.style.display = 'none'
        }else{
            loggedInNavbarArrowUp.style.display = 'none'
            loggedInNavbarArrowDown.style.display = 'flex'
        }
    })
}


navLinkSearchButton.addEventListener('click', (e) => {
    searchFormWrapper.classList.toggle('show-search-form-wrapper')
})

// searchFormCloseButton.addEventListener('click', (e) => {
//     searchFormWrapper.classList.toggle('show-search-form-wrapper')
// })

mobileNavLinkSearchButton.addEventListener('click', (e) => {
    searchFormWrapper.classList.toggle('show-search-form-wrapper')
    mobileSearchFormContainer.classList.toggle('show-mobile-search-form-container')
    mobileNavLinks.classList.remove('show-mobile-nav-bar')
    mobileNavBackgroundLayout.style.display = 'none'
    body.style.overflow = 'auto'

})

if(toggleUserNavbar) {
    window.addEventListener('click', (e) => {
        if(e.target != loggedInNavbarUserProfileImg &&
            e.target != loggedInNavbarUsername &&
            e.target != loggedInNavbarArrowUp &&
            e.target != loggedInNavbarArrowDown
        ){
            if(!loggedInUserNavLinks.classList.contains('show-logged-in-user-nav-links')) {
                loggedInNavbarArrowUp.style.display = 'none'
                loggedInNavbarArrowDown.style.display = 'flex'
            }
            else {
                loggedInUserNavLinks.classList.remove('show-logged-in-user-nav-links')
                loggedInNavbarArrowUp.style.display = 'none'
                loggedInNavbarArrowDown.style.display = 'flex'
            }
        }
    })
}

window.addEventListener('resize', (e) => {
    searchFormWrapper.classList.remove('show-search-form-wrapper')
    mobileSearchFormContainer.classList.remove('show-mobile-search-form-container')
    if(loggedInUserNavLinks){
        loggedInUserNavLinks.classList.remove('show-logged-in-user-nav-links')
    }
    mobileNavLinks.classList.remove('show-mobile-nav-bar')
    mobileNavBackgroundLayout.style.display = 'none'
    body.style.overflow = 'auto'
})

/*
=============
BANNER IMAGES
=============
*/

let index = 0

TranslateBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
        const targetElement = e.currentTarget === bannerArrowLeft ? bannerArrowLeft : bannerArrowRight
        if(targetElement === bannerArrowLeft){
            index --
        }else if(targetElement === bannerArrowRight) {
            index ++
        }
        if(index < 0){
            index = bannerImgContainers.length - 1
        }else if(index > bannerImgContainers.length - 1){
            index = 0
        }
        bannerImgContainers.forEach((img) => {
            img.style.transform = `translate(-${index * 100}%)`
        })
    })
})


/*
===================
PRODUCT DETAIL PAGE
===================
*/ 

productDetailToggleBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
        const element = e.currentTarget
        if(element.classList.contains('product-description-drop')){
            if(productDescription.classList.contains('hide-product-description')){
                productDescription.classList.remove('hide-product-description')
                productDescriptionArrowDown.style.display = 'none'
                productDescriptionArrowUp.style.display = 'flex'
            }else{
                productDescription.classList.add('hide-product-description')
                productDescriptionArrowDown.style.display = 'flex'
                productDescriptionArrowUp.style.display = 'none'
            }
        }else if(element.classList.contains('product-detail-drop')) {
            if(productDetail.classList.contains('hide-product-detail')) {
                productDetail.classList.remove('hide-product-detail')
                productDetailArrowDown.style.display = 'none'
                productDetailArrowUp.style.display = 'flex'
            }else {
                productDetail.classList.add('hide-product-detail')
                productDetailArrowDown.style.display = 'flex'
                productDetailArrowUp.style.display = 'none'
            }
        }
    })
})


/*
=================================
PRODUCT DETAIL PAGE EXTRAN IMAGES
=================================
*/ 


productDetailExtraImage.forEach((img) => {
    img.addEventListener('click', (e) => {
        const targetElement = e.currentTarget
        const childElement = targetElement.querySelector('.extra-image')
        const closeBtn = targetElement.querySelector('.product-detail-image-close-btn')
        if(!targetElement.classList.contains('extra-image-full-screen')){
            targetElement.classList.add('extra-image-full-screen')
            childElement.classList.add('image-full-screen')
            body.style.overflow = 'hidden'
            closeBtn.style.display = 'block'
            body.scrollTop(0)
        }else{
            targetElement.classList.remove('extra-image-full-screen')
            childElement.classList.remove('image-full-screen')
            body.style.overflow = 'auto'
            closeBtn.style.display = 'none'
        }
    })
})


/*
===================================
PRODUCT LIST PAGE RATING STAR ICONS
=================================== */

 const productLikeContainer = document.querySelectorAll('.product-like-container')

for(let num = 0; num < productLikeContainer.length; num++){

    const ratingNum = productLikeContainer[num].firstElementChild
    const rateStarIcons = productLikeContainer[num].querySelector('.rate-star-icons')
    
    let firstNum = ''
    let lastNum = ''

    if(ratingNum){
        firstNum = parseInt(ratingNum.textContent.slice(0,-2))
        lastNum = parseInt(ratingNum.textContent.slice(-1))
    }

    let add = ''

    for(let rateNum = 0; rateNum < firstNum; rateNum++) {
        add += '<span class="material-symbols-rounded like-icon">star</span>'
    }
    if (lastNum){
        add += '<span class="material-symbols-rounded like-icon">star_half</span>'
    }
   
    rateStarIcons.innerHTML += add
}

/*
=====================================
PRODUCT DETAIL PAGE RATING STAR ICONS
===================================== */

const productDetailFavoriteIconContainer = document.querySelector('.product-detail-favorite-icon-container')
const productDetailRatingCount = document.querySelector('.product-detail-rating-count')

if(productDetailFavoriteIconContainer) {

    let first_num = productDetailRatingCount.textContent.slice(0, -2)
    let second_num = productDetailRatingCount.textContent.slice(-1)
    let start = ''

    for(let i = 0; i < parseInt(first_num); i++){
        start += '<span class="material-symbols-rounded product-detail-favorite-icon">star</span>'
    }
    if(parseInt(second_num)){
        start += '<span class="material-symbols-rounded product-detail-favorite-icon">star_half</span>'
    }
    productDetailFavoriteIconContainer.innerHTML += start
}