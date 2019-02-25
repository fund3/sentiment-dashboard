angular.module('BitcoinSentimentsApp', [])
.factory('BitcoinSentimentsService', ['$q', '$rootScope', function($q, $rootScope) {
  var Service = {}

  Service.getTweetsFromServer = function() {
      url = '/get_tweets.json'
      var promise = fetch(url)
      return promise;
  }

  Service.getMeanSentsFromServer = function() {
      url = '/get_mean_sentiments.json'
      var promise = fetch(url)
      return promise;
  }

  return Service;
}])
.controller('TweetTableController', function($scope, BitcoinSentimentsService) {
    var tweetTable = this;

    tweetTable.tweets = [];

    tweetTable.showTimeline = function() {
        if($('#card_li_plot a').hasClass('bs_timeline_empty') && $('#card_li_intro a').hasClass('active')) {
            $('#card_li_intro a').removeClass('active')
            $('#card_li_plot a').addClass('active')
            $('#card_body_intro').css('display', 'none')
            $('#card_body_plot').css('display', 'block')

            tweetTable.tweets = [
                {'id_str': 1, 'full_text': 'working!'}
            ]

            // Get sentiment ticks quicker:
            BitcoinSentimentsService.getMeanSentsFromServer()
            .then(function(response) {
                return response.json()
            }).then(function(data) {
                $('#plot_card_spinner').css('display', 'none')
                Bokeh.embed.embed_item(data['mean_sentiments_plot'], 'mean_sentiments_plot_div')
                $scope.$apply();
            })

            BitcoinSentimentsService.getTweetsFromServer()
            .then(function(response) {
                return response.json()
            }).then(function(data) {
//                $('#plot_card_spinner').css('display', 'none')
//                Bokeh.embed.embed_item(data['ih_sentiments_plot'], 'mainplot_div')
                tweetTable.tweets = data['tweets']
                $scope.$apply();
            })

            $('#card_li_plot a').removeClass('bs_timeline_empty')
        } else {
            $('#card_li_intro a').removeClass('active')
            $('#card_li_plot a').addClass('active')
            $('#card_body_intro').css('display', 'none')
            $('#card_body_plot').css('display', 'block')
        }
    };

    tweetTable.getIntro = function() {
        if($('#card_li_plot a').hasClass('active')) {
            $('#card_li_plot a').removeClass('active')
            $('#card_li_intro a').addClass('active')
            $('#card_body_plot').css('display', 'none')
            $('#card_body_intro').css('display', 'block')
        }
    };

});
