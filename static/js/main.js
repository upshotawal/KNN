console.log('Thank You for the Rating')

const one = document.getElementById('first')
const two = document.getElementById('second')
const three = document.getElementById('third')
const four = document.getElementById('fourth')
const five = document.getElementById('fifth')


const form = document.querySelector('.rate-form')
let rating = 0;

const csrf = document.getElementsByName('csrfmiddlewaretoken')
    // console.log(form)
    // console.log(confirmBox)
    // console.log(csrf)


const handleStarSelector = (size) => {
    const children = form.children
    for (let i = 0; i < children.length; i++) {
        if (i <= size) {
            children[i].classList.add('checked')
        } else {
            children[i].classList.remove('checked')
        }
    }
}


const handleSelect = (selection) => {
    switch (selection) {
        case 'first':
            {
                // one.classList.add('checked')
                // two.classList.remove('checked')
                // three.classList.remove('checked')
                // four.classList.remove('checked')
                // five.classList.remove('checked')
                handleStarSelector(1)
                rating = 1;
                break;

            }
        case 'second':
            {

                handleStarSelector(2)
                rating = 2;
                break;

            }
        case 'third':
            {
                handleStarSelector(3)
                rating = 3;
                break;

            }
        case 'fourth':
            {
                handleStarSelector(4)
                rating = 4;
                break;

            }
        case 'fifth':
            {
                handleStarSelector(5)
                rating = 5;
                break;

            }
    }
}

const getNumericValue = (stringValue) => {

    console.log(stringValue)
    if (stringValue === 'first') {
        numericValue = 1
    } else if (stringValue === 'second') {
        numericValue = 2
    } else if (stringValue === 'third') {
        numericValue = 3
    } else if (stringValue === 'fourth') {
        numericValue = 4
    } else if (stringValue === 'fifth') {
        numericValue = 5
    } else {
        numericValue = 0
    }
    console.log(numericValue)
    return numericValue
}

if (one) {
    const arr = [one, two, three, four, five]

    arr.forEach(item => item.addEventListener('mouseover', (event) => { handleSelect(event.target.id) }))

    arr.forEach(item => item.addEventListener('click', (event) => {
        const val = event.target.id
        console.log(val)

        alert('Rating has been Submitted ')
        form.addEventListener('submit', e => {
            e.preventDefault()
            console.log(rating)
            const id = e.target.id;
            console.log("id:", id)
            console.log(typeof(rating));
            console.log(typeof(id));
            console.log(id);

            $.ajax({
                type: 'POST',
                url: '/rate/',
                data: {
                    'csrfmiddlewaretoken': csrf[0].value,
                    'el_id': id,
                    'val': rating,
                },
                success: function(responce) {
                    console.log(responce)

                },
                error: function(error) {
                    console.log(error)

                }
            })

        })

    }))

}