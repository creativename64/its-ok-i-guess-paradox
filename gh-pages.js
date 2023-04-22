var ghpages = require('gh-pages');

ghpages.publish(
    'public',
    {
        branch: 'gh-pages',
        repo: 'https://github.com/creativename64.git', 
        user: {
            name: 'neop',
            email: 'gaelanhortness@gmail.com'
        }
    },
    () => {
        console.log('Deploy Complete!')
    }
)