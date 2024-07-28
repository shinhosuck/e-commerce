
// mobile navigation
const mobileNavs = [...document.querySelectorAll('.mobile-nav')]
const mobileNavLinks = document.querySelector('.mobile-nav-links-wrapper')
const mobileToggleNavBtn = document.querySelector('.mobile-toggle-nav-btn')

// search form
const searchFormContainer = document.querySelector('.search-form-container')
const searchBtns = [...document.querySelectorAll('.search-btn')]

// product detail extra images
const productDetailImageContainer = document.querySelector('.product-detail-img-container')
const imageFullScreen = document.querySelector('.product-detail-fullscreen-images-container')
const fullScreenCloseBtn = document.querySelector('.fullscreen-close-btn')
const fullScreenExtraImages = document.querySelectorAll('.fullscreen-extra-image')
const fullScreenImage = document.querySelector('.fullscreen-image')


const body = document.querySelector('body')


// show or hide mobile navlinks
if (mobileToggleNavBtn) {
    const children = [...mobileToggleNavBtn.children]
    children.forEach((btn)=> {
        btn.addEventListener('click', (e)=> {
            if(e.currentTarget.classList.contains('open-mobile-nav-btn')) {
                mobileNavLinks.classList.add('show-mobile-nav-bar')
                e.currentTarget.classList.add('hide-mobile-navlink-toggle-btn')
                e.currentTarget.nextElementSibling.classList.remove('hide-mobile-navlink-toggle-btn')
            }else if(e.currentTarget.classList.contains('close-mobile-nav-btn')) {
                mobileNavLinks.classList.remove('show-mobile-nav-bar')
                e.currentTarget.previousElementSibling.classList.remove('hide-mobile-navlink-toggle-btn')
                e.currentTarget.classList.add('hide-mobile-navlink-toggle-btn')
            }
        })
    })
}
    

// show or hide search form
searchBtns.forEach((btn)=> {
    btn.addEventListener('click', (e)=> {
        searchFormContainer.classList.toggle('show-search-form-container')
    })
})


// product detail extra images 
function handleImages(e) {

        const childEl = fullScreenImage.querySelector('img')
        const img = e.currentTarget.querySelector('img')

        const fullscreenSrc = childEl.src
        const extraImageSrc = img.src

        // img.src = fullscreenSrc
        childEl.src = extraImageSrc
}

productDetailImageContainer && productDetailImageContainer.addEventListener('click', (e)=> {
    imageFullScreen.classList.add('show-product-detail-image-fullscreen')
    window.scrollTo({top:62, behavior:'instant'})
    body.style.overflow = 'hidden'
    fullScreenExtraImages.forEach((img, index)=>{
        img.addEventListener('click', handleImages)
    })
})

fullScreenCloseBtn && fullScreenCloseBtn.addEventListener('click', ()=> {
    imageFullScreen.classList.remove('show-product-detail-image-fullscreen')
    body.style.overflow = 'scroll'
})

// end product detail extra images 