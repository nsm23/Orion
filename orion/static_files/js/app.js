$(document).ready(function () {
    bind_show_reply_form() // показ формы ответа
    bind_hide_reply_form() // скрытие формы ответа при фокусе на поле нового коммента
    bind_save_comment() // сохранение коммента
    bind_comment_validation() // валидцая формы сохранения коммента
});

bind_hide_reply_form = function () {
    if ($('.comments-textarea[hide-reply="true"]').length >= 1) {
        $('.comments-textarea[hide-reply="true"]').on('focus', function () {
            hide_all_reply_forms()
        })
    }
}

bind_show_reply_form = function () {
    $('.reply-link').each(function (_, elem) {
        $(elem).on('click', function () {
            show_reply_form(elem)
        })
    })
}

hide_all_reply_forms = function () {
    $('.reply-form').addClass('d-none')
}

bind_save_comment = function () {
    $('.btn-comment-save').each(function (_, elem) {
        $(elem).on('click', function () {
            save_comment(elem)
        })
    })
}

bind_comment_validation = function () {
    $('.comments-textarea').each(function (_, elem) {
        $(elem).on('input propertychange', function () {
            validate_comment_text(elem)
        })
    })
}

/**
 * Показывает форму ответа при клике на "Ответить"
 */
show_reply_form = function (elem) {
    hide_all_reply_forms()

    var comment_id = $(elem).data('comment_id') ?? 0
    if (comment_id <= 0) return false;

    if ($('#reply-to-' + comment_id + '-form').length > 0) {
        $('#reply-to-' + comment_id + '-form').removeClass('d-none')

        $('#reply-to-' + comment_id + '-form').find('.comments-textarea').focus()
    }
}

save_comment = function (elem) {
    var comment_form = $(elem).closest('.comment-form')
    if (comment_form.length > 0) {
        var comment_textarea = comment_form.find('.comments-textarea') ?? ''
        var post_id = comment_form.data('post_id') ?? 0
        var parent_id = comment_form.data('parent_id') ?? 0
        if (comment_textarea.length > 0 && post_id > 0) {
            var comment_text = comment_textarea.val() ?? ''
            var btn_comment_save = comment_form.find('.btn-comment-save') ?? ''

            if ($.trim(comment_text) !== '') {
                $.ajax({
                    url: '/comments/save/',
                    method: 'post',
                    data: {
                        text: comment_text,
                        post: post_id,
                        parent: parent_id,
                        csrfmiddlewaretoken: Cookies.get('csrftoken'),
                    },
                    error: function (jqXHR, error, errorThrown) {
                        comment_textarea.attr('readonly', false)
                        if (btn_comment_save.length > 0) {
                            btn_comment_save.attr('disabled', false)
                            btn_comment_save.html('Отправить <i class="fas fa-long-arrow-alt-right ms-1"></i>')
                        }

                        if (jqXHR.status && jqXHR.status === 400) {
                            alert(jqXHR.responseText);
                        }
                        else if (jqXHR.status === 403) {
                            alert("У вас недостаточно прав доступа!")
                        }
                        else {
                            alert("Something went wrong")
                        }
                    },
                    success: function (json) {
                        comment_textarea.val('')
                        comment_textarea.attr('readonly', false)
                        if (btn_comment_save.length > 0) {
                            btn_comment_save.attr('disabled', false)
                            btn_comment_save.html('Отправить <i class="fas fa-long-arrow-alt-right ms-1"></i>')
                        }

                        if (parent_id > 0) {
                            $('#reply-to-' + parent_id + '-form').addClass('d-none')
                            $('#reply-to-' + parent_id + '-form').parent().append(json.html)
                        } else {
                            var comments_exists = $('#post-comments').find('.comments').length > 0 ? true : false
                            var comment_html = '<div class="comments d-flex flex-start' + (comments_exists ? ' mt-4' : '') + '">' + json.html + '</div>'
                            if (comments_exists) {
                                $('#post-comments').append(comment_html)
                            } else {
                                $('#post-comments').html(comment_html)
                            }

                            $('#comment-' + json.comment_id).find('.reply-link').on('click', function () {
                                show_reply_form($(this))
                            })

                            $('#reply-to-' + json.comment_id + '-form').find('.comments-textarea').on('input propertychange', function () {
                                validate_comment_text($(this))
                            })

                            $('#reply-to-' + json.comment_id + '-form').find('.btn-comment-save').on('click', function () {
                                save_comment($(this))
                            })
                        }
                    },
                    beforeSend: function () {
                        comment_textarea.attr('readonly', true)
                        if (btn_comment_save.length > 0) {
                            btn_comment_save.attr('disabled', true)
                            btn_comment_save.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Сохранение...')
                        }
                    },
                });
            }
        }
    }
}

validate_comment_text = function (elem) {
    var comment_text = $(elem).val() ?? ''

    var invalid = false
    if ($.trim(comment_text) == '') {
        invalid = true
    }

    $(elem).closest('.comment-form').find('.btn-comment-save').attr('disabled', invalid)
}

tinyMCE.init({
    selector: '.tinymce',
    theme: "silver",
    menubar: false,
    language: 'ru',
    plugins: [
        'advlist autolink lists link image charmap print preview anchor',
        'searchreplace visualblocks code fullscreen',
        'insertdatetime media table paste code help wordcount'
    ],
    toolbar: 'undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help'
});

function formatReactionBtn(reactionBtn, reactionType) {
    /**
     * Format reaction buttons (like or dislike):
     * * toggle a color of a clicked button icon between colored (green for like and red for dislike) and uncolored
     * (gray) via Bootstrap classes;
     * * toggle the clicked button icon between filled and unfilled
     * * set a color of the opposite button (like vs. dislike) as uncolored
     * * set an icon of the opposite button (like vs. dislike) as unfilled
     * */

    const LIKE_CLASSES = {
        coloredTextClass: "text-success",
        uncoloredTextClass: "text-secondary",
        filledIconClass: "bi-hand-thumbs-up-fill",
        unfilledIconClass: "bi-hand-thumbs-up",
    }
    const DISLIKE_CLASSES = {
        coloredTextClass: "text-danger",
        uncoloredTextClass: "text-secondary",
        filledIconClass: "bi-hand-thumbs-down-fill",
        unfilledIconClass: "bi-hand-thumbs-down",
    }

    let reactionBtnClasses, oppositeReactionBtnClasses, oppositeReactionSelector;
    if (reactionType === "like") {
        reactionBtnClasses = LIKE_CLASSES;
        oppositeReactionBtnClasses = DISLIKE_CLASSES;
        oppositeReactionSelector = ".dislike-btn";
    } else if (reactionType === "dislike") {
        reactionBtnClasses = DISLIKE_CLASSES;
        oppositeReactionBtnClasses = LIKE_CLASSES;
        oppositeReactionSelector = ".like-btn";
    }
    const reactionBtnIcon = reactionBtn.querySelector('i');
    const oppositeReactionBtn = reactionBtn.parentElement.querySelector(oppositeReactionSelector);
    const oppositeReactionBtnIcon = oppositeReactionBtn.querySelector('i');

    reactionBtn.classList.toggle(reactionBtnClasses.coloredTextClass);
    reactionBtn.classList.toggle(reactionBtnClasses.uncoloredTextClass);
    reactionBtnIcon.classList.toggle(reactionBtnClasses.filledIconClass);
    reactionBtnIcon.classList.toggle(reactionBtnClasses.unfilledIconClass);

    oppositeReactionBtn.classList.remove(oppositeReactionBtnClasses.coloredTextClass);
    oppositeReactionBtn.classList.add(oppositeReactionBtnClasses.uncoloredTextClass);
    oppositeReactionBtnIcon.classList.remove(oppositeReactionBtnClasses.filledIconClass);
    oppositeReactionBtnIcon.classList.add(oppositeReactionBtnClasses.unfilledIconClass);
}

function reaction(reactionBtn, reactionType) {
    const type = reactionBtn.dataset.type;
    const pk = reactionBtn.dataset.id;
    const action = reactionBtn.dataset.action;

    $.ajax({
        url: "/" + type + "/" + pk + "/" + action + "/",
        type: 'POST',
        data: {'obj': pk, 'csrfmiddlewaretoken': Cookies.get('csrftoken')},

        success: function (json) {
            const sum_rating = JSON.parse(json).sum_rating;
            const like_total = document.querySelector('#like-total');

            like_total.innerHTML = sum_rating > 0 ? '+' : '';
            like_total.innerHTML += sum_rating;
            formatReactionBtn(reactionBtn, reactionType);
        }
    });
    return false;
}

function like() {
    return reaction($(this)[0], "like");
}

function dislike() {
    return reaction($(this)[0], "dislike");
}

function speech() {
  const slug = $(this).data('id');
  const textToSpeech = $('.card-text').text();
  const spinner = $('#spinner')

  spinner.addClass('fa fa-spinner fa-spin')

  $.ajax({
      url: "/posts/speech/" + slug,
      type: 'POST',
      data: {
        'csrfmiddlewaretoken': Cookies.get('csrftoken'),
        'text': textToSpeech,
    },
    success: function (speechFilePath) {
      $('#speech-button').remove()
      spinner.removeClass( "fa fa-spinner fa-spin" )
      file = window.location.origin + '/media/' + speechFilePath

      const audio = $(`<audio controls><source id="source" src="${file}" type="audio/mpeg">Your browser does not support the audio element.</audio>`)
      $("#audio-container").append(audio)
    }
  });
}


function complaint_save() {
  const complaint_form = $('div.complaint-form')
  const post_id = complaint_form.data('post_id') ?? 0
  const complaint_text = $('.complaint-textarea')
  const submit_btn = $('.btn-complaint-save')
  const data = {
    text: complaint_text.val(),
    post: post_id,
    csrfmiddlewaretoken: Cookies.get('csrftoken'),
  }

  $.ajax({
    url: '/complaints/save/',
    method: 'post',
    data: data,
    error: function (jqXHR, error, errorThrown) {
        if (jqXHR.status && jqXHR.status == 400) {
            alert(jqXHR.responseText);
        } else {
            alert("Something went wrong")
        }
    },
    success: function (json) {
        complaint_text.val('')
        const success_message = $(`
          <div class="alert alert-success complaint-success" role="alert">
            Ваша жалоба успешно принята
          </div>
        `)
        $('.complaint-container').append(success_message)
        $('button.complaint-toggle').css('display', 'block')
        $('.complaint-form').css('display', 'none')
    }
  });
}

function complaint_toggle() {
  $('button.complaint-toggle').css('display', 'none')
  $('.complaint-form').css('display', 'block')
  if ($('.complaint-success').length){
    $('.complaint-success').remove()
  }
}

validate_complaint_text = function() {
    var complaint_text = $('.complaint-textarea').val() ?? ''

    var invalid = false
    if ($.trim(complaint_text) == '') {
        invalid = true
    }
    $('.btn-complaint-save').attr('disabled', invalid)
}

// Подключение обработчиков
$(function () {
    $('[data-action="like"]').click(like);
    $('[data-action="dislike"]').click(dislike);
    $('[data-action="speech"]').click(speech);
    $('button.complaint-toggle').click(complaint_toggle);
    $('button.btn-complaint-save').click(complaint_save);
    $('.complaint-textarea').bind('input propertychange', validate_complaint_text)
});
